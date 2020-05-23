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



## Similar tools
- https://github.com/sindresorhus/trash-cli
- https://github.com/ali-rantakari/trash
- https://gist.github.com/dabrahams/14fedc316441c350b382528ea64bc09c
