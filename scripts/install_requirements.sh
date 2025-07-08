while IFS= read -r package; do
    pip install "$package"
    if [ $? -ne 0 ]; then
        echo "Installation failed for package: $package"
        break
    fi
done < requirements.txt
