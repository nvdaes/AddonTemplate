# Updating an Existing Add-on

As AddonTemplate evolves, it receives improvements, bug fixes, new GitHub workflows, and build system updates.

If your add-on was created from an older version of AddonTemplate, you can merge the latest template changes into your repository instead of manually copying updated files.

This document explains the recommended update procedure.

> [!NOTE]
> Updating from AddonTemplate only affects your project's infrastructure (build scripts, GitHub workflows, configuration files, etc.). It does **not** modify your add-on's source code.

## Before you begin

Before updating your repository:

- Ensure your working tree is clean.

  ```
  git status
  ```

- Commit or stash any pending changes.

- It is recommended to perform the update on a dedicated branch.

If anything goes wrong before the merge commit is created, you can safely cancel the operation using:

```
git merge --abort
```

## Adding the template repository

If you have not already done so, add AddonTemplate as a remote:

```
git remote add template https://github.com/nvaccess/AddonTemplate.git
```

Then fetch the latest changes:

```
git fetch template
```

## Merging the latest template

Merge the latest version of AddonTemplate:

```
git merge template/master --allow-unrelated-histories
```

The `--allow-unrelated-histories` option is required because your add-on repository and AddonTemplate do not share a common Git history.

At this stage, Git may report merge conflicts.

This is completely normal.

## Understanding merge conflicts

During the merge, Git attempts to combine the contents of both repositories automatically.

When Git cannot determine which version should be kept, it reports a merge conflict.

A conflict does **not** mean that something went wrong.
It simply means that some files require manual review.

## Resolving the merge

### Keep your add-on documentation

Your add-on documentation should not be replaced by the template.

Restore the following files from your current branch:

```
git restore --source=HEAD README.md CHANGELOG.md
```

### Remove the template documentation

The `docs/` directory belongs to AddonTemplate itself.

It is not intended to become part of your add-on repository.

Remove it:

```
git rm -r docs
```

### Resolve buildVars.py

`buildVars.py` usually contains merge conflicts because it includes both:

- information specific to your add-on;
- variables introduced by newer versions of AddonTemplate.

Review the file carefully.

In general:

- keep your add-on metadata;
- preserve your version number;
- keep your custom settings;
- add any new variables introduced by the template.

### Resolve pyproject.toml

`pyproject.toml` is another file that commonly requires manual review.

Keep your project-specific configuration while incorporating any new settings required by the updated template.

### Other files

For most remaining files, the version provided by AddonTemplate is generally the correct one.

Typical examples include:

- `.github/`
- `.gitignore`
- `manifest.ini.tpl`
- `manifest-translated.ini.tpl`
- `site_scons/`
- `sconstruct`

Review any conflicts if necessary before completing the merge.

## Completing the merge

Once all conflicts have been resolved, stage the modified files:

```
git add .
```

Then create the merge commit:

```
git commit
```

## Summary

| File or directory | Recommended action |
|-------------------|--------------------|
| `README.md` | Keep the add-on version |
| `CHANGELOG.md` | Keep the add-on version |
| `docs/` | Remove |
| `buildVars.py` | Merge manually |
| `pyproject.toml` | Merge manually |
| Other template files | Usually accept the template version |

## Troubleshooting

### I don't understand a merge conflict

Merge conflicts are expected when updating from a newer version of AddonTemplate.

Most conflicts occur in `buildVars.py` and `pyproject.toml`.

Review the conflicting sections carefully and combine the changes from both versions.

### I want to cancel the update

If you have not yet committed the merge, you can restore your repository to its previous state:

```
git merge --abort
```