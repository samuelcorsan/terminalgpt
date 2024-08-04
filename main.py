import subprocess
import sys
import platform
from openai import OpenAI

client = OpenAI(
    api_key="openai_api_key"
)

def generate_command(prompt, os_type):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are an expert assistant in programming and command generation who converts requests into terminal commands for {os_type}. You should always return only the command necessary to fulfill the user's request. You should not provide explanations, additional descriptions, or use markdown. Just the command and nothing else. DO NOT USE MARKDOWN like ```bash``` in your response, only the command."},
            {"role": "user", "content": f"Here is my request, never refuse, if it is something very advanced try it, YOU ALWAYS CAN, you are an expert in this: {prompt}"}
        ],
        temperature=0.7, 
        max_tokens=4096
    )
    
    command = response.choices[0].message.content.strip()
    return command

def write_and_open_file(filename, content, os_type):
    try:
        # Write the content to the file
        with open(filename, 'w') as file:
            file.write(content)

        # Command to open the file in a text editor
        if os_type == "Windows":
            open_command = f"notepad {filename}"
        elif os_type == "Darwin":  # macOS
            open_command = f"open -a TextEdit {filename}"
        elif os_type == "Linux":
            open_command = f"xdg-open {filename}"
        else:
            print("Unsupported operating system.")
            return

        # Execute the command to open the file
        subprocess.run(open_command, shell=True)
    except Exception as e:
        print(f"Error writing or opening the file: {e}")

def execute_command(command):
    """
    Executes a command in the system and allows direct interaction with the terminal.
    """
    try:
        # Execute the command and allow direct interaction with the terminal
        result = subprocess.run(command, shell=True, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error executing the command: {e}")
        return -1

def main():
    os_type = platform.system()  # Detect the operating system
    
    while True:
        user_input = input("What do you want to do? ")

        # Generate content based on the user's description
        prompt = f"Convert the following description into a terminal command: {user_input}"
        command = generate_command(prompt, os_type)
        
        print(f"Generated command: {command}")

        # Check if the user is asking for file creation
        if "echo " in command and " > " in command:
            # Extract the content to write and the filename
            parts = command.split(" > ")
            if len(parts) == 2:
                content = parts[0].replace('echo ', '').strip().strip('"')
                filename = parts[1].strip()

                # Replace '\n' with actual newlines
                content = content.replace("\\n", "\n")

                # Write the content to the file and open it
                write_and_open_file(filename, content, os_type)
            else:
                print("Error in the command format.")
        else:
            # Execute the command as usual
            exit_code = execute_command(command)
            print(f"The command was executed with exit code: {exit_code}")

        continue_prompt = input("Do you want to do something else? (yes/no): ")
        if continue_prompt.lower() != 'yes':
            break

if __name__ == "__main__":
    main()
