from os import system
processes_to_kill=["Firefox"]
for pro in range(len(processes_to_kill)):
    system(f"taskkill /f /im  {processes_to_kill[pro]}.exe")

    #wsl --shutdown
    #  in pwsh for Vmmem - linux subsystem related to docker