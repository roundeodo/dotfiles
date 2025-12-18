#!/usr/bin/env bash
DOTFILES_DIR=$(cd $(dirname $0); pwd)

files="bashrc aliases vimrc"

echo "starting configuration"

for file in $files; do
	[-f ~/.$file] && mv ~/.$file ~/.$file.bak

	ln -s $DOTFILES_DIR/$file ~/.$file
	echo "linked $file"
done

echo "configuration is done"
