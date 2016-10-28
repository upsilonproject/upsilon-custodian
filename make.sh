#!/bin/bash

rm -rf pkg 
mkdir -p pkg

buildid -n
buildid -qf rpmmacro -W .buildid.rpmmacro

BUILD_DIR=upsilon-custodian-`buildid -k tag`
mkdir -p $BUILD_DIR

cp -r .buildid .buildid.rpmmacro src var $BUILD_DIR/

zip -r upsilon-custodian.zip $BUILD_DIR

rm -rf $BUILD_DIR
