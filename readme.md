# Trash101
Unlike other trash cli tools, trash101:
- Works properly with `sudo`
  - Files still get moved to your normal user trash location
  - You won't get an additional GUI password prompt
  - Respects sudoers
- Isn't slowed down by applescript
- Provides a `putback` command that restores trashed files to their original locations
  - (Doesn't enable the Put Back menu item in Finder, but *no* tools can do that without
  causing the issues above)

The trash path is currently mac-specific; PRs accepted for other platforms.

## Installing

Via [pipx](https://github.com/pipxproject/pipx):

    brew install pipx
    pipx ensurepath
    pipx install trash101


## Usage
    trash ~/some/file.ext
    putback ~/.Trash/file.ext


## FAQ
**Does the `putback` command work with files that were trashed via Finder?**

It doesn't. The only way to do that is via applescript, which is slow and doesn't
work well with sudo. I experimented with implementing it by mimicking what Finder
does internally (getting the original location from the trash's .DS_Store file),
but that is problematic as well, because Finder takes a while before flushing
changes to that file, making it impossible to get the data for recently trashed
files.

For the same reason, attempting to write put-back data to the .DS_Store file
(in the `trash` command) would be problematic.


## Similar tools
- https://github.com/sindresorhus/trash-cli
- https://github.com/ali-rantakari/trash
- https://gist.github.com/dabrahams/14fedc316441c350b382528ea64bc09c
