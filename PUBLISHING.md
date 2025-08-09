# Publishing Guide for @yourusername/server-toggl

## Prerequisites

1. **npm account**: You need an npm account
2. **GitHub repository**: Your code should be in a public GitHub repository

## Steps to Publish

### 1. Setup Your Package

Run the setup script to configure the package with your npm username:

```bash
./setup-npm-package.sh
```

This will:
- Check if you're logged into npm
- Update package.json with your actual npm username
- Update the README with your username

### 2. Login to npm

```bash
npm login
```

### 3. Update Package Information

After running the setup script, update the following in `package.json`:

- Replace `"Your Name"` with your actual name
- Update the repository URL to point to your actual GitHub repository
- Update the version number if needed

### 4. Test the Package Locally

```bash
# Build the package
npm run build

# Test the binary
node dist/index.js
```

### 5. Publish to npm

```bash
npm publish --access public
```

## Package Name

Your package will be published under your own npm scope as `@yourusername/server-toggl`. This is the recommended approach as it gives you full control over your package.

Users will install it with:
```bash
npm install -g @yourusername/server-toggl
```

## Usage After Publishing

Once published, users can install and use your package:

```bash
# Install globally
npm install -g @yourusername/server-toggl

# Or use with npx
npx -y @yourusername/server-toggl
```

## Claude Desktop Configuration

Users can add this to their Claude Desktop config:

```json
{
  "mcpServers": {
    "toggl": {
      "command": "npx",
      "args": ["-y", "@yourusername/server-toggl"],
      "env": {
        "TOGGL_API_TOKEN": "your_toggl_api_token_here"
      }
    }
  }
}
```

## Updating the Package

To update the package:

1. Make your changes
2. Update the version in `package.json`
3. Build: `npm run build`
4. Publish: `npm publish`

## Troubleshooting

### Permission Denied
If you get permission errors, make sure you're logged in to npm.

### Python Not Found
The package requires Python to be installed. Make sure users have Python 3.8+ installed and accessible via the `python` command.

### Dependencies
The package will automatically install Python dependencies when first run, but users need to have pip available.
