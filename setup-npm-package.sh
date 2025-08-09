#!/bin/bash

# Setup script for npm package publishing
echo "🚀 Setting up npm package for publishing..."

# Check if npm is logged in
if ! npm whoami > /dev/null 2>&1; then
    echo "❌ You're not logged into npm. Please run: npm login"
    exit 1
fi

# Get npm username
NPM_USERNAME=$(npm whoami)
echo "✅ Logged in as: $NPM_USERNAME"

# Update package.json with actual username
echo "📝 Updating package.json with your npm username..."
sed -i.bak "s/@yourusername/@$NPM_USERNAME/g" package.json
rm package.json.bak

# Update README with actual username
echo "📝 Updating NPM_README.md with your npm username..."
sed -i.bak "s/@yourusername/@$NPM_USERNAME/g" NPM_README.md
rm NPM_README.md.bak

# Update repository URL if needed
echo "📝 Please update the repository URL in package.json to point to your actual GitHub repository"
echo "   Current: https://github.com/yourusername/admin-toggl-mcp"
echo "   Update to: https://github.com/$NPM_USERNAME/admin-toggl-mcp (or your actual repo URL)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the repository URL in package.json"
echo "2. Update the author name in package.json"
echo "3. Test the build: npm run build"
echo "4. Publish: npm publish --access public"
echo ""
echo "Your package will be published as: @$NPM_USERNAME/server-toggl"
