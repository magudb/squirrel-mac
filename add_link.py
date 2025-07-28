#!/usr/bin/env python3
import json
import sys
import os
import subprocess
import argparse
import re
import traceback
from datetime import datetime

def load_categories():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    categories_file = os.path.join(script_dir, 'categories.json')
    try:
        with open(categories_file, 'r') as f:
            data = json.load(f)
            return data['categories']
    except FileNotFoundError:
        print(f"Error: {categories_file} not found!")
        sys.exit(1)

def save_categories(categories):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    categories_file = os.path.join(script_dir, 'categories.json')
    data = {'categories': categories}
    with open(categories_file, 'w') as f:
        json.dump(data, f, indent=2)

def display_categories(categories):
    print("\nAvailable categories:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat['name']}")
    print(f"{len(categories) + 1}. Add new category")

def add_new_category():
    print("\n--- Add New Category ---")
    name = input("Enter category name: ").strip()
    if not name:
        print("Category name cannot be empty!")
        return None
    
    anchor = input("Enter anchor ID (e.g., 'devops', 'tools'): ").strip().lower()
    if not anchor:
        anchor = name.lower().replace(' ', '-').replace(',', '')
    
    return {
        'id': anchor,
        'name': name,
        'anchor': anchor
    }

def format_link(url, title, selected_text=None):
    if selected_text and selected_text.strip():
        return f"- [{selected_text}]({url}){{:target=\"_blank\"}}"
    return f"- [{title}]({url}){{:target=\"_blank\"}}"

def add_link_to_blog(category, link_text, blog_file=None):
    if not blog_file:
        blog_file = input("\nEnter blog post file path (or press Enter for 'blog_post.md'): ").strip()
        if not blog_file:
            blog_file = 'blog_post.md'
    
    if not os.path.exists(blog_file):
        print(f"Blog file '{blog_file}' not found. Creating template...")
        create_blog_template(blog_file)
        return
    
    with open(blog_file, 'r') as f:
        content = f.read()
    
    # Find the section for the category
    anchor_pattern = f'<a name="{category["anchor"]}"></a>'
    anchor_index = content.find(anchor_pattern)
    
    if anchor_index == -1:
        print(f"Warning: Anchor '{anchor_pattern}' not found in blog file.")
        print("Please manually add the link to the appropriate section.")
        print(f"\nFormatted link:\n{link_text}")
        return
    
    # Find where to insert the link
    section_start = anchor_index
    next_section = content.find('\n##', section_start + 1)
    if next_section == -1:
        next_section = len(content)
    
    # Find the last link in the section
    section_content = content[section_start:next_section]
    lines = section_content.split('\n')
    
    # Find the last line that starts with "- ["
    insert_position = section_start
    for i, line in enumerate(lines):
        if line.strip().startswith('- ['):
            # Find this line in the original content
            line_pos = content.find(line, insert_position)
            if line_pos != -1:
                insert_position = line_pos + len(line)
    
    # Insert the new link
    if insert_position == section_start:
        # No existing links, add after the header
        header_end = content.find('\n', section_start)
        if header_end != -1:
            insert_position = header_end
    
    # Add the link
    new_content = content[:insert_position] + '\n' + link_text + content[insert_position:]
    
    with open(blog_file, 'w') as f:
        f.write(new_content)
    
    print(f"\nLink added to '{category['name']}' section in {blog_file}")

def create_blog_template(filename):
    template = """---
layout: post
title: "Tech Digest: Curated Insights"
description: "Stay ahead with this curated collection of impactful articles and resources."
comments: false
category: "Curated Insights"
keywords: "Software Development, Leadership, DevOps"
---

<!-- markdownlint-disable MD033 MD020 MD025-->
# My favorites<a name="favorites"></a>

## Agile, Leadership and Product<a name="agile"></a>

## Architecture, Development & Software development practices<a name="development"></a>

## DevOps, Observability & Security<a name="devops"></a>

## Tools and things from Github<a name="tools"></a>
"""
    
    with open(filename, 'w') as f:
        f.write(template)
    print(f"Created blog template: {filename}")

def show_category_dialog(categories, url, title):
    """Show category selection dialog using osascript with dropdown"""
    # Create list of category names for the dropdown
    category_names = [cat['name'] for cat in categories]
    category_names.append("➕ Add new category...")
    
    # Format the list for AppleScript
    category_list_str = ', '.join([f'"{name}"' for name in category_names])
    
    script = f'''tell application "System Events"
    activate
    set categoryList to {{{category_list_str}}}
    set selectedCategory to choose from list categoryList with title "Select Category" with prompt "Choose a category for this link:" default items {{item 1 of categoryList}} without multiple selections allowed
    
    if selectedCategory is false then
        return ""
    else
        return item 1 of selectedCategory
    end if
end tell'''
    
    try:
        log_error(f"Running osascript for category dialog")
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        log_error(f"Osascript result: returncode={result.returncode}, stdout='{result.stdout}', stderr='{result.stderr}'")
        
        if result.returncode == 0:
            selected = result.stdout.strip()
            if selected:
                # Find which category was selected
                for i, cat in enumerate(categories):
                    if cat['name'] == selected:
                        return str(i + 1)
                if selected == "➕ Add new category...":
                    return str(len(categories) + 1)
        return None
    except Exception as e:
        log_error(f"Error in show_category_dialog: {str(e)}\n{traceback.format_exc()}")
        return None

def log_error(error_msg):
    """Log errors to a file for debugging"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, 'add_link_errors.log')
    
    with open(log_file, 'a') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Error at {datetime.now()}\n")
        f.write(f"{error_msg}\n")
        f.write(f"{'='*50}\n")

def show_notification(message, title="Link Added"):
    """Show macOS notification"""
    # Escape quotes in message for AppleScript
    message = message.replace('"', '\\"')
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script])

def find_curated_insights_files(drafts_dir):
    """Find all draft files with category: 'Curated Insights'"""
    curated_files = []
    
    if not os.path.exists(drafts_dir):
        return curated_files
    
    for filename in os.listdir(drafts_dir):
        if filename.endswith('.md') or filename.endswith('.markdown'):
            filepath = os.path.join(drafts_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Check if file has 'category: "Curated Insights"' in front matter
                    if 'category: "Curated Insights"' in content:
                        # Extract title from front matter
                        title_match = re.search(r'title:\s*["\'](.+?)["\']', content)
                        title = title_match.group(1) if title_match else filename
                        curated_files.append({
                            'path': filepath,
                            'filename': filename,
                            'title': title
                        })
            except Exception:
                continue
    
    return curated_files

def show_file_selection_dialog(files):
    """Show file selection dialog using osascript with dropdown"""
    # Create list of file descriptions for the dropdown
    file_descriptions = [f"{f['filename']} - {f['title']}" for f in files]
    
    # Format the list for AppleScript
    file_list_str = ', '.join([f'"{desc}"' for desc in file_descriptions])
    
    script = f'''tell application "System Events"
    set fileList to {{{file_list_str}}}
    set selectedFile to choose from list fileList with title "Select Blog File" with prompt "Multiple 'Curated Insights' files found. Choose one:" default items {{item 1 of fileList}} without multiple selections allowed
    
    if selectedFile is false then
        return ""
    else
        return item 1 of selectedFile
    end if
end tell'''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0:
        selected = result.stdout.strip()
        if selected:
            # Find which file was selected
            for i, desc in enumerate(file_descriptions):
                if desc == selected:
                    return str(i + 1)
    return None

def browser_mode(url, title, selected_text=None, blog_file=None):
    """Handle link addition from browser via osascript"""
    try:
        log_error(f"Loading categories...")
        categories = load_categories()
        log_error(f"Loaded {len(categories)} categories")
        
        # Show category selection dialog
        log_error(f"Showing category dialog...")
        choice_str = show_category_dialog(categories, url, title)
        log_error(f"Category dialog returned: {choice_str}")
        if not choice_str:
            log_error("User cancelled category selection")
            return
    except Exception as e:
        error_msg = f"Error loading categories or showing dialog: {str(e)}\n{traceback.format_exc()}"
        log_error(error_msg)
        show_notification("Error loading categories. Check add_link_errors.log", "Error")
        return
    
    try:
        choice = int(choice_str)
        if 1 <= choice <= len(categories):
            selected_category = categories[choice - 1]
        elif choice == len(categories) + 1:
            # Handle new category via dialog
            script = '''tell application "System Events"
                set categoryName to text returned of (display dialog "Enter new category name:" default answer "" with title "New Category")
                set categoryAnchor to text returned of (display dialog "Enter anchor ID (e.g., 'devops', 'tools'):" default answer "" with title "New Category")
                return categoryName & "|" & categoryAnchor
            end tell'''
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                name, anchor = result.stdout.strip().split('|')
                if not anchor:
                    anchor = name.lower().replace(' ', '-').replace(',', '')
                new_category = {
                    'id': anchor,
                    'name': name,
                    'anchor': anchor
                }
                categories.append(new_category)
                save_categories(categories)
                selected_category = new_category
            else:
                return
        else:
            show_notification("Invalid category selection", "Error")
            return
    except ValueError as e:
        error_msg = f"Invalid category selection: {choice_str}\n{str(e)}"
        log_error(error_msg)
        show_notification("Invalid category selection", "Error")
        return
    except Exception as e:
        error_msg = f"Error in category selection: {str(e)}\n{traceback.format_exc()}"
        log_error(error_msg)
        show_notification("Error selecting category. Check add_link_errors.log", "Error")
        return
    
    try:
        # Format and add the link
        link_text = format_link(url, title, selected_text)
        
        # Find blog file if not specified
        if not blog_file:
            home_dir = os.path.expanduser('~')
            drafts_dir = os.path.join(home_dir, 'Documents/projects/magudb.github.io/_drafts')
        
        # Find all files with category: "Curated Insights"
        curated_files = find_curated_insights_files(drafts_dir)
        
        if len(curated_files) == 0:
            # No curated insights files found, use default
            blog_file = os.path.join(drafts_dir, 'linkblog.md')
        elif len(curated_files) == 1:
            # Only one file found, use it
            blog_file = curated_files[0]['path']
        else:
            # Multiple files found, ask user to choose
            choice_str = show_file_selection_dialog(curated_files)
            if not choice_str:
                return
            
            try:
                choice = int(choice_str) - 1
                if 0 <= choice < len(curated_files):
                    blog_file = curated_files[choice]['path']
                    # Log which file was selected
                    log_msg = f"Selected blog file: {blog_file}"
                    log_error(log_msg)
                else:
                    show_notification("Invalid file selection", "Error")
                    return
            except ValueError:
                show_notification("Invalid file selection", "Error")
                return
    except Exception as e:
        error_msg = f"Error finding blog files: {str(e)}\n{traceback.format_exc()}"
        log_error(error_msg)
        show_notification("Error finding blog files. Check add_link_errors.log", "Error")
        return
    
    # Add to blog file
    try:
        if not os.path.exists(blog_file):
            error_msg = f"Blog file not found: {blog_file}"
            log_error(error_msg)
            show_notification(f"Blog file not found: {os.path.basename(blog_file)}", "Error")
            return
            
        with open(blog_file, 'r') as f:
            content = f.read()
        
        # Check for duplicate
        if url in content:
            show_notification("Link already exists in blog", "Duplicate Link")
            return
        
        # Find the section for the category
        anchor_pattern = f'<a name="{selected_category["anchor"]}"></a>'
        anchor_index = content.find(anchor_pattern)
        
        if anchor_index == -1:
            show_notification(f"Category section not found: {selected_category['name']}", "Error")
            return
        
        # Find where to insert the link
        section_start = anchor_index
        next_section = content.find('\n##', section_start + 1)
        if next_section == -1:
            next_section = len(content)
        
        # Find the last link in the section
        section_content = content[section_start:next_section]
        lines = section_content.split('\n')
        
        # Find the last line that starts with "- ["
        insert_position = section_start
        for i, line in enumerate(lines):
            if line.strip().startswith('- ['):
                # Find this line in the original content
                line_pos = content.find(line, insert_position)
                if line_pos != -1:
                    insert_position = line_pos + len(line)
        
        # Insert the new link
        if insert_position == section_start:
            # No existing links, add after the header
            header_end = content.find('\n', section_start)
            if header_end != -1:
                insert_position = header_end
        
        # Add the link
        new_content = content[:insert_position] + '\n' + link_text + content[insert_position:]
        
        with open(blog_file, 'w') as f:
            f.write(new_content)
        
        show_notification(f"Added to {selected_category['name']}", "Link Added")
        
        # Log success
        log_msg = f"Success: Added link to {selected_category['name']} in {blog_file}\nURL: {url}\nTitle: {title}"
        log_error(log_msg)  # Using same log file for success too
        
    except Exception as e:
        error_msg = f"Error adding link to blog: {str(e)}\n{traceback.format_exc()}\nBlog file: {blog_file}\nURL: {url}\nCategory: {selected_category}"
        log_error(error_msg)
        show_notification("Error adding link. Check add_link_errors.log", "Error")

def main():
    print("=== Link Blog Category Manager ===")
    
    # Get link details
    url = input("Enter link URL: ").strip()
    if not url:
        print("URL cannot be empty!")
        return
    
    title = input("Enter link title: ").strip()
    if not title:
        print("Title cannot be empty!")
        return
    
    # Load categories
    categories = load_categories()
    
    # Display categories and get selection
    while True:
        display_categories(categories)
        
        try:
            choice = int(input("\nSelect category (number): "))
            
            if 1 <= choice <= len(categories):
                selected_category = categories[choice - 1]
                break
            elif choice == len(categories) + 1:
                # Add new category
                new_category = add_new_category()
                if new_category:
                    categories.append(new_category)
                    save_categories(categories)
                    print(f"\nAdded new category: {new_category['name']}")
                    selected_category = new_category
                    break
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
    
    # Format the link
    link_text = format_link(url, title)
    
    print(f"\nAdding to category: {selected_category['name']}")
    print(f"Formatted link: {link_text}")
    
    # Ask if user wants to add to blog file
    add_to_file = input("\nAdd to blog file? (y/n): ").strip().lower()
    if add_to_file == 'y':
        add_link_to_blog(selected_category, link_text)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Add links to blog with categories')
        parser.add_argument('--url', help='URL to add')
        parser.add_argument('--title', help='Link title')
        parser.add_argument('--selected', help='Selected text (optional)')
        parser.add_argument('--blog', help='Blog file path (optional)')
        parser.add_argument('--browser', action='store_true', help='Browser mode (use dialogs)')
        
        args = parser.parse_args()
        
        # Log the arguments received
        if args.browser:
            log_msg = f"Started with args: url={args.url}, title={args.title}, selected={args.selected}, blog={args.blog}"
            log_error(log_msg)
        
        if args.browser and args.url and args.title:
            # Called from osascript with browser data
            browser_mode(args.url, args.title, args.selected, args.blog)
        else:
            # Interactive mode
            main()
    except Exception as e:
        error_msg = f"Fatal error in main: {str(e)}\n{traceback.format_exc()}"
        log_error(error_msg)
        if '--browser' in sys.argv:
            show_notification("Fatal error. Check add_link_errors.log", "Error")
        else:
            print(f"Fatal error: {e}")
        sys.exit(1)