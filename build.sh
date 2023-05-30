commit_hash=$(git rev-parse --short HEAD)
dist_name="stupid-simple-image-labels-"$commit_hash
pyinstaller app.py --name $dist_name --onefile --add-data "static:static" --add-data "templates:templates"