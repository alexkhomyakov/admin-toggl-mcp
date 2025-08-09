#!/usr/bin/env node

import { spawn, execSync } from 'child_process';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Get the path to the Python connector
const connectorPath = join(__dirname, '..', 'connector.py');

// Try multiple Python paths in order of preference
const pythonPaths = [
  // 1. Try to find a virtual environment in the current directory
  join(process.cwd(), '.venv', 'bin', 'python'),
  join(process.cwd(), 'venv', 'bin', 'python'),
  join(process.cwd(), 'env', 'bin', 'python'),
  // 2. Try to find a virtual environment in the package directory
  join(__dirname, '..', '.venv', 'bin', 'python'),
  join(__dirname, '..', 'venv', 'bin', 'python'),
  join(__dirname, '..', 'env', 'bin', 'python'),
  // 3. Fall back to system Python
  'python3',
  'python'
];

// Find the first available Python executable
let pythonExecutable = 'python3'; // fallback
for (const path of pythonPaths) {
  if (path.includes('venv') || path.includes('env')) {
    if (existsSync(path)) {
      pythonExecutable = path;
      break;
    }
  } else {
    // For system Python, try to execute it
    try {
      execSync(`${path} --version`, { stdio: 'ignore' });
      pythonExecutable = path;
      break;
    } catch {
      continue;
    }
  }
}

// If we're using system Python, try to create a virtual environment
if (!pythonExecutable.includes('venv') && !pythonExecutable.includes('env')) {
  console.error('System Python detected, creating virtual environment...');
  
  // Try multiple locations for the virtual environment
  const venvLocations = [
    join(process.cwd(), '.mcp-venv'),
    join(process.env.HOME || process.env.USERPROFILE || '', '.mcp-venv'),
    join(process.env.TMPDIR || '/tmp', '.mcp-venv')
  ];
  
  let venvPath = null;
  let venvPythonPath = null;
  
  // Find a writable location
  for (const location of venvLocations) {
    try {
      if (!existsSync(location)) {
        console.error(`Creating virtual environment at: ${location}`);
        execSync(`${pythonExecutable} -m venv ${location}`, { stdio: 'inherit' });
        console.error('Virtual environment created successfully');
      }
      venvPath = location;
      venvPythonPath = join(location, 'bin', 'python');
      break;
    } catch (error) {
      console.error(`Failed to create virtual environment at ${location}:`, error);
      continue;
    }
  }
  
  if (venvPythonPath && existsSync(venvPythonPath)) {
    pythonExecutable = venvPythonPath;
    console.error('Using created virtual environment');
  }
}

console.error(`Using Python executable: ${pythonExecutable}`);

// Check if required Python packages are installed
const requirementsPath = join(__dirname, '..', 'requirements.txt');
if (existsSync(requirementsPath)) {
  try {
    console.error('Checking Python dependencies...');
    execSync(`${pythonExecutable} -c "import mcp"`, { stdio: 'ignore' });
    console.error('MCP package found');
  } catch {
    console.error('Installing Python dependencies...');
    try {
      // Install dependencies without --user flag if in virtual environment
      const isVenv = pythonExecutable.includes('venv') || pythonExecutable.includes('env');
      const userFlag = isVenv ? '' : '--user ';
      execSync(`${pythonExecutable} -m pip install ${userFlag}-r ${requirementsPath}`, { 
        stdio: ['inherit', 'pipe', 'inherit'],
        cwd: process.cwd()
      });
    } catch (error) {
      console.error('Failed to install dependencies:', error);
      console.error('Trying alternative installation method...');
      try {
        // Try installing just the essential packages
        const isVenv = pythonExecutable.includes('venv') || pythonExecutable.includes('env');
        const userFlag = isVenv ? '' : '--user ';
        execSync(`${pythonExecutable} -m pip install ${userFlag}mcp`, { 
          stdio: ['inherit', 'pipe', 'inherit'],
          cwd: process.cwd()
        });
      } catch (error2) {
        console.error('Failed to install MCP package:', error2);
        process.exit(1);
      }
    }
  }
}

// Spawn the Python process
const pythonProcess = spawn(pythonExecutable, [connectorPath], {
  stdio: ['inherit', 'inherit', 'inherit'],
  cwd: process.cwd()
});

// Handle process events
pythonProcess.on('error', (error) => {
  console.error('Failed to start Python connector:', error);
  process.exit(1);
});

pythonProcess.on('exit', (code) => {
  process.exit(code || 0);
});

// Handle SIGINT and SIGTERM
process.on('SIGINT', () => {
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  pythonProcess.kill('SIGTERM');
});
