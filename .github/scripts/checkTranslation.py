# checkTranslation.py
import sys
import os
from crowdin_api import CrowdinClient


def findFileId(client: CrowdinClient, project_id: int, base_target: str, search_ext: str) -> int | None:
	"""
	Iterates through all project files (using pagination) to find the ID
	of the source file matching the target name and extension.
	
	@param client: The Crowdin API client instance.
	@type client: CrowdinClient
	@param project_id: The ID of the Crowdin project.
	@type project_id: int
	@param base_target: The base name of the file (e.g., 'myaddon').
	@type base_target: str
	@param search_ext: The extension to look for (e.g., '.pot').
	@type search_ext: str
	@return: The file ID if found, otherwise None.
	@rtype: int | None
	"""
	offset = 0
	limit = 100

	while True:
		resp = client.source_files.list_files(
			projectId=project_id,
			limit=limit,
			offset=offset,
		)

		data = resp["data"]
		for f in data:
			path_crowdin = f["data"]["path"].lower()
			# Check if the path ends with addon_id.pot or addon_id.xliff
			if path_crowdin.endswith(f"{base_target}{search_ext}"):
				file_id = f["data"]["id"]
				print(f"DEBUG: Match found: {path_crowdin} (ID: {file_id})")
				return file_id

		if len(data) < limit:
			break

		offset += limit

	return None


def getScoreFromAPI(file_name_to_search: str, lang_id: str) -> float:
	"""
	Retrieves the translation progress score for a specific language and file.
	Handles pagination for both file listing and language status.
	
	@param file_name_to_search: The local path or name of the file to check.
	@type file_name_to_search: str
	@param lang_id: The language code (e.g., 'fr' or 'pt_BR').
	@type lang_id: str
	@return: The translation ratio between 0.0 and 1.0.
	@rtype: float
	"""
	token = os.environ.get("crowdinAuthToken")
	p_id_env = os.environ.get("CROWDIN_PROJECT_ID")

	if not token or not p_id_env:
		print("ERROR: Missing environment variables 'crowdinAuthToken' or 'CROWDIN_PROJECT_ID'.")
		return 0.0

	client = CrowdinClient(token=token)
	p_id = int(p_id_env)

	try:
		# Clean and prepare search patterns
		# Example: 'addon/locale/fr/LC_MESSAGES/myaddon.po' -> base_target: 'myaddon'
		base_target = file_name_to_search.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0].lower()
		ext_target = file_name_to_search.split(".")[-1].lower()

		# On Crowdin, the source for a .po file is usually a .pot file
		search_ext = ".pot" if ext_target == "po" else f".{ext_target}"

		print(f"DEBUG: Searching for source file: {base_target}{search_ext}")

		file_id = findFileId(client, p_id, base_target, search_ext)

		if file_id is None:
			print(f"WARNING: File '{base_target}{search_ext}' not found on Crowdin.")
			return 0.0

		# Pagination for translation status (Progress)
		offset = 0
		limit = 100

		while True:
			resp = client.translation_status.get_file_progress(
				projectId=p_id,
				fileId=file_id,
				limit=limit,
				offset=offset,
			)

			data = resp["data"]
			for item in data:
				lang_api = item["data"]["languageId"]

				# Flexible matching (e.g., 'fr' will match 'fr' or 'fr-FR' from API)
				# Also handles underscore to dash conversion for Crowdin compatibility
				if lang_api.lower().startswith(lang_id.lower().replace("_", "-")):
					progress = float(item["data"]["translationProgress"])
					return progress / 100

			# Check pagination total
			total = resp["pagination"]["totalCount"]
			if offset + limit >= total:
				break
			offset += limit

		print(f"DEBUG: Language '{lang_id}' not found in progress list for this file.")
		return 0.0

	except Exception as e:
		print(f"API ERROR: {e}")
		return 0.0


def main():
	if len(sys.argv) < 3:
		print("Usage: python checkTranslation.py <file_path> <lang_id>")
		sys.exit(2)

	input_file = sys.argv[1]
	lang = sys.argv[2]

	score = getScoreFromAPI(input_file, lang)

	# Output formatted for capture by the PowerShell script
	print(f"translationRatio={score}")

	# Identify extension to provide a specific score label
	ext = input_file.lower().split('.')[-1]
	if ext == 'md':
		print(f"mdScore={score}")
	elif ext == 'xliff':
		print(f"xliffScore={score}")
	else:
		# Default to poScore for .po and other localization files
		print(f"poScore={score}")

	# Exit with success (0) if there is at least 50% translated content
	sys.exit(0 if score > 0.5 else 1)

if __name__ == "__main__":
	main()
