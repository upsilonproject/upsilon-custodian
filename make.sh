#!/bin/bash

buildid -n
buildid -qf rpmmacro -W .buildid.rpmmacro

BUILD_DIR=upsilon-custodian-`buildid -k tag`
mkdir -p $BUILD_DIR

cp -r .buildid .buildid.rpmmacro src var etc $BUILD_DIR/

rm -rf build/distributions/
mkdir -p build/distributions/

zip -r build/distributions/upsilon-custodian.zip $BUILD_DIR

rm -rf $BUILD_DIR
