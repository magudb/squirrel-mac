# Squirrel Mac - Jekyll Blog Link Collector

A Mac OS utility that captures URLs from your browser and automatically adds them to your Jekyll blog drafts with smart categorization.

## Features

- **Multi-Browser Support**: Works with Safari, Chrome, Microsoft Edge, and Firefox
- **Quick Capture**: Grab URL and title from your browser with a keyboard shortcut
- **Smart Categorization**: Automatically determines which section of your blog the link belongs to based on URL patterns
- **Selected Text Support**: If you have text selected in the browser, it will be used as the link text (Safari, Chrome, Edge only)
- **Duplicate Detection**: Prevents adding the same URL twice
- **Jekyll Format**: Links are formatted with Jekyll/Markdown syntax including `{:target="_blank"}`

## Installation

1. **Clone or download this repository** to `/Users/magnusudbjorg/Documents/projects/squirrel-mac/`

2. **Make scripts executable**:
   ```bash
   chmod +x add_to_blog.applescript
   chmod +x append_link.sh
   ```

3. **Create the Automator Quick Action**:
   
   a. Open Automator (found in Applications)
   
   b. Choose "File" → "New" → "Quick Action"
   
   c. Configure the workflow:
      - Set "Workflow receives" to "no input" in "any application"
      - Drag "Run Shell Script" action from the library
      - Set Shell to `/bin/bash`
      - Enter this command:
        ```
        osascript /Users/magnusudbjorg/Documents/projects/squirrel-mac/add_to_blog.applescript
        ```
   
   d. Save as "Add to Blog" (or your preferred name)

4. **Assign a keyboard shortcut**:
   
   a. Open System Settings → Keyboard → Keyboard Shortcuts → Services
   
   b. Find "Add to Blog" under General
   
   c. Click "Add Shortcut" and press your desired key combination (e.g., ⌘⇧L)

## Usage

1. Navigate to any webpage in Safari, Chrome, Edge, or Firefox
2. (Optional) Select specific text to use as the link text (not supported in Firefox)
3. Press your keyboard shortcut
4. You'll see a notification confirming the link was added

### Browser-Specific Notes

- **Safari, Chrome, Edge**: Full support including selected text capture
- **Firefox**: Limited support - captures URL and title only, no selected text. The browser window will briefly activate to copy the URL

## How It Works

### Smart Categorization

The tool automatically categorizes links into these sections:

- **My favorites**: Special/highlighted links (manually managed)
- **Agile, Leadership and Product**: Links about agile, scrum, leadership, management, team culture
- **Architecture, Development & Software development practices**: Programming, APIs, design patterns, testing
- **DevOps, Observability & Security**: Kubernetes, Docker, monitoring, CI/CD, security tools
- **Tools and things from Github**: GitHub/GitLab repositories and tools

### File Structure

- `add_to_blog.applescript`: Main script that captures browser info
- `append_link.sh`: Shell script that handles file manipulation and categorization
- `create_automator_workflow.sh`: Helper to set up Automator (optional)

## Customization

### Change Target Blog File

Edit line 4 in `add_to_blog.applescript`:
```applescript
set blogDraftPath to "/path/to/your/draft.md"
```

### Modify Categorization Rules

Edit the `determine_section()` function in `append_link.sh` to add your own URL patterns and categorization logic.

### Add New Sections

1. Add the section to your Jekyll draft
2. Update the case statement in `append_link.sh` with the new section header

## Troubleshooting

### "Operation not permitted" error
- Go to System Settings → Privacy & Security → Automation
- Allow Terminal/Automator to control Safari/Chrome/Edge/Firefox
- For Firefox, also allow "System Events" under Accessibility

### Links not appearing
- Check that the draft file path is correct
- Ensure the section headers in your draft match exactly (including "##" prefix)
- Run the AppleScript directly in Script Editor to see detailed errors

### Keyboard shortcut not working
- Ensure the Automator workflow is saved in ~/Library/Services/
- Check that the shortcut isn't conflicting with other apps
- Try logging out and back in to refresh services

### Firefox-specific issues
- Firefox requires GUI scripting, so the browser window must be visible
- If URL capture fails, ensure Firefox has focus when using the shortcut
- Selected text is not supported due to Firefox's limited AppleScript support
- Consider using Safari, Chrome, or Edge for full functionality

## Technical Details

- Uses AppleScript to interface with browsers
- Shell script for file manipulation (more reliable than AppleScript for text processing)
- Supports Safari, Chrome, Microsoft Edge (full AppleScript support) and Firefox (GUI scripting)
- Automatically detects which browser is active and uses the first available
- Non-destructive: creates temp files before modifying your draft

## Future Enhancements

- Support for more browsers (Brave, Arc, Opera)
- Improved Firefox support if AppleScript API becomes available
- Custom categories via configuration file
- Menu bar app version
- Integration with other note-taking systems