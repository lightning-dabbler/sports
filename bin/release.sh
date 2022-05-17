#!/usr/bin/env bash

repo_version=v0.2.0

git-tag(){
    git tag $repo_version
}

git-tag-force(){
    git tag --force $repo_version
}

push-git-tag(){
    git push origin $repo_version
}

push-git-tag-force(){
    git push --force origin $repo_version
}

get-git-hash(){
    echo `git rev-parse --short HEAD`
}

build-main-image(){
    if [ $# -eq 0 ] || ! [ "$1" == "deployment" ]; then
        TAG=$repo_version.`get-git-hash` docker-compose -f docker-compose/main.yaml --project-directory . build
    else
        TAG=$repo_version docker-compose -f docker-compose/main.yaml --project-directory . build --force-rm --no-cache
    fi
}

enter-main-image(){
    TAG=$repo_version.`get-git-hash` docker-compose -f docker-compose/main.yaml --project-directory . run --rm sports-main bash
}

"$@"
