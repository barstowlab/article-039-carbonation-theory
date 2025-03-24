# List of Functions for the Multiparameter Sweep 

# Function to Run Terminal Commands; For executing CrunchTope 
def run_command(command):
    # Import the necessary Python Libraries 
    import subprocess
    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)   
    except subprocess.CalledProcessError as e:
        # Handle errors in the called command
        print("Error executing command:")
        print(e)
        print("STDERR:")
        print(e.stderr)

# A Function to Run the Input Files InitialStage.in and NaOHStage.in one after the other 
# and piece the two resulting two series to form a continuous time series and outputs this continuous time series

def Time_Series(PestControl, Initial_NaOH, Initial_Magnesium, Initial_Seed_Volume):
    # PestControl is the PestControl.ant file used to specify the input file being ran 
    # Initial_NaOH is the specified NaOH concentration 
    # Initial_Magnesium is the specified Magnesium concentration
    # Initial_Seed_Volume is the specified Magnesite Seed that you start with 

    import pandas as pd
    import re
    import subprocess
    import threading

    # *** you will need to specify path to your crunch executable to run
    # properly!!! ***
    crunch_exe_path = '/Users/user/Documents/crunchtope/M1MacPre-compiled/CrunchTope-Mac'

    # Run the InitialStage file 
    Pest = open(PestControl, "r+") # open the file for read and write mode
    Pest.seek(0)
    data = Pest.readlines()
    if len(data) > 0:
        data[0] = "InitialStage.in\n"
    else:
        print(f"Error: Not enough lines in the file, current length is {len(data)}")
    
    Pest.close()
    Pest = open(PestControl, "w")
    Pest.writelines(data)
    Pest.close()

    InitialStage = open("InitialStage.in", "r+") # open the file for read and write mode
    InitialStage.seek(0) # ensure that the file is being read from the top
    data = InitialStage.readlines()

    Initial_Magnesium = str(Initial_Magnesium)

    # Define the Magnesium Pattern to Modify 
    patterns = {
        'Mg++': r"^Mg\+\+\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?"
    }

    # Modify the Magnesium line based on the initial Mg concentration stated 
    for i, line in enumerate(data):
        for compound, pattern in patterns.items():
            if re.match(pattern, line.strip()):
                if compound == 'Mg++':
                    data[i] = f"Mg++             {Initial_Magnesium}\n"

    InitialStage.close() # close before reopening in writing mode 

    InitialStage = open("InitialStage.in", "w")
    
    InitialStage.writelines(data) # write in the new Magnesium concentration into the Input File 
    
    InitialStage.close()

    # run the terminal command to execute crunchtope simulation for InitialStage file 
    proc = subprocess.Popen(crunch_exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    nice = threading.Timer(80, proc.terminate) # if model takes longer than ~1 minute to run, terminate and move on
    nice.start()
    mean = threading.Timer(130, proc.kill)
    mean.start()

    # Monitor the output for the error message
    while True:
        # Capture the output and error from stdout and stderr, decoding them to strings
        output = proc.stdout.readline().decode('utf-8')
        error_output = proc.stderr.readline().decode('utf-8')

        # If no more output and the process has finished, break the loop
        if output == '' and error_output == '' and proc.poll() is not None:
            break  # Process finished
        
        # Check if the specific error message is in the output
        if '-->EXCEEDED MAXIMUM ITERATIONS IN CONDITION: stage1' in output:
            print("Error: Exceeded maximum iterations. Terminating process.")
            proc.terminate()  # Terminate the process immediately
            # Run clean-up commands if needed
            run_command("rm *rst")
            run_command("rm *out")
            run_command("clear")
            return  # Exit the function after terminating the process 
            

    proc.wait()
    nice.cancel()
    mean.cancel()

    if proc.returncode is not None and proc.returncode != 0:
        print("Process was terminated due to timeout. Exiting function.")
        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 
        return  # Exit the function if the process was terminated

    # Read text file into database 
    Initial_Input = pd.read_fwf("magnesitebatch.out")

     # Delete all the NaN columns
    Initial_Input.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6', 'Column7', 'Column8', 'Column9','Column10', 'Column11']
    Initial_Input = Initial_Input.drop(['Column1', 'Column3', 'Column4', 'Column5'], axis = 1)
    Initial_Input.columns = ['Time(hrs)', 'SiO2(aq)', 'Mg++', 'Gluconic acid(aq)', 'CO2(aq)', 'Na+', 'pH']
    Initial_Input = Initial_Input.drop(index = 0)

    # Convert all values in the DataFrame to numeric
    Initial_Input = Initial_Input.apply(pd.to_numeric, errors='coerce')

    # Obtain the Magnesite Volume Fraction for the InitialStage Run
    volume1 = pd.read_fwf('volume1.out')

    volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4']
    volume1 = volume1.drop(index = 0)
    volume1 = volume1.drop(index = 1)

    volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

    volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
    volume1 = volume1.rename(columns={'Column3': 'Quartz'})
    volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})

    # Convert all values in the DataFrame to numeric
    volume1 = volume1.apply(pd.to_numeric, errors='coerce')

    # Pass these two volume fractions on from the initialstage 
    Quartz_volume_fraction = volume1['Quartz'].iloc[0] / 100
    Amorphous_Silica_volume_fraction = volume1['Amorphous Silica'].iloc[0] / 100

    # Delete the output files and clear the terminal 
    run_command("rm *rst")
    run_command("rm *out")
    run_command("clear") 

    # Run the NaOHStage Input File 

    Pest = open(PestControl, "r+") # open the file for read and write mode
    Pest.seek(0)
    data = Pest.readlines()
    if len(data) > 0:
        data[0] = "NaOHStage.in\n"
    else:
        print(f"Error: Not enough lines in the file, current length is {len(data)}")
    
    Pest.close()
    Pest = open(PestControl, "w")
    Pest.writelines(data)
    Pest.close()

    # Edit the Initial Concentrations in the NaOHStage.in Input File 
    Magnesium_concentration = Initial_Input['Mg++'].iloc[-1] * 1000
    SiO2_concentration = Initial_Input['SiO2(aq)'].iloc[-1] * 1000 
    Gluconic_acid_concentration = Initial_Input['Gluconic acid(aq)'].iloc[-1] * 1000 

    NaOHStage = open("NaOHStage.in", "r+") # open the file for read and write mode
    NaOHStage.seek(0) # ensure that the file is being read from the top
    data = NaOHStage.readlines()

    Magnesium_concentration = str(Magnesium_concentration)
    SiO2_concentration = str(SiO2_concentration)
    Gluconic_acid_concentration = str(Gluconic_acid_concentration)
    Initial_NaOH = str(Initial_NaOH) # Pass the NaOH Input into the NaOHStage.in 

    # Define the patterns for each line to modify
    patterns = {
    'Mg++': r"^Mg\+\+\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'SiO2(aq)': r"^SiO2\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'Gluconic_acid(aq)': r"^Gluconic_acid\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'Na+': r"^Na\+\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?"
    }

    # Modify each line based on the patterns defined above
    for i, line in enumerate(data):
        for compound, pattern in patterns.items():
            if re.match(pattern, line.strip()):
                if compound == 'Mg++':
                    data[i] = f"Mg++             {Magnesium_concentration}\n"
                elif compound == 'SiO2(aq)':
                    data[i] = f"SiO2(aq)        {SiO2_concentration}\n"
                elif compound == 'Gluconic_acid(aq)':
                    data[i] = f"Gluconic_acid(aq) {Gluconic_acid_concentration}\n"
                elif compound == 'Na+':
                    data[i] = f"Na+             {Initial_NaOH}\n"
                break  # Exit after the first match for this line

    ## Edit the volume fractions in the NaOHstage.in Input File 
    # Define a dictionary to map mineral names to their corresponding regex patterns

    Magnesite_volume_fraction = str(Initial_Seed_Volume) # Set the Seed Volume at the start 
    Quartz_volume_fraction = str(Quartz_volume_fraction)
    Amorphous_Silica_volume_fraction = str(Amorphous_Silica_volume_fraction)

    
    # Create a dictionary to hold the volume fractions
    volume_fractions = {
        'Magnesite': Magnesite_volume_fraction,
        'Quartz': Quartz_volume_fraction,
        'Amorphous_Silica': Amorphous_Silica_volume_fraction
    }

    # Check for zero values in the volume fraction and replace them otherwise the Crunchtope Model will not run 
    for mineral, volume in volume_fractions.items():
        if volume in ['0.0', '0', '0.00', '0.000']:
            volume_fractions[mineral] = '1.0e-10'

    # Unpack the updated values back into the original variables
    Magnesite_volume_fraction = volume_fractions['Magnesite']
    Quartz_volume_fraction = volume_fractions['Quartz']
    Amorphous_Silica_volume_fraction = volume_fractions['Amorphous_Silica']

    patterns = {
        'Magnesite': r"^Magnesite\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Quartz': r"^Quartz\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Amorphous_silica': r"^Amorphous_silica\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$"
    }

    # Initialize a dictionary to store the mineral names and their corresponding matched indices
    matched_indices = {}

    # Loop through the file lines already stored in `data` and match each one against the patterns
    for i, line in enumerate(data):
        for mineral, pattern in patterns.items():
            if re.match(pattern, line.strip()):
                # Store the index in the dictionary with the mineral as the key
                if mineral not in matched_indices:
                    matched_indices[mineral] = []
                matched_indices[mineral].append(i)  # Append the index to the list for that mineral

    # Modify the corresponding lines in the data based on matched indices
    for mineral, indices in matched_indices.items():
        for index in indices:
            # print(f"{mineral} line found at index {index}: {data[index].strip()}")

            # Modify the line with the appropriate volume fraction
            if mineral == 'Magnesite':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Magnesite_volume_fraction, data[index], count=1)
            elif mineral == 'Quartz':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Quartz_volume_fraction, data[index], count=1)
            elif mineral == 'Amorphous_silica':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Amorphous_Silica_volume_fraction, data[index], count=1)

            # Update the data at that index with the modified line
            data[index] = modified_line
            #print(f"Modified line: {data[index].strip()}")
        
    NaOHStage.close() # close before reopening in writing mode 

    NaOHStage = open("NaOHStage.in", "w")
    
    NaOHStage.writelines(data) # write in the new concentration into the Input File 
    
    NaOHStage.close()

    # run the terminal command to execute crunchtope simulation for NaOH file 
    proc = subprocess.Popen(crunch_exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    nice = threading.Timer(80, proc.terminate) # if model takes longer than ~1 minute to run, terminate and move on
    nice.start()
    mean = threading.Timer(130, proc.kill)
    mean.start()

    # Monitor the output for the error message
    while True:
        # Capture the output and error from stdout and stderr, decoding them to strings
        output = proc.stdout.readline().decode('utf-8')
        error_output = proc.stderr.readline().decode('utf-8')

        # If no more output and the process has finished, break the loop
        if output == '' and error_output == '' and proc.poll() is not None:
            break  # Process finished
        
        # Check if the specific error message is in the output
        if '-->EXCEEDED MAXIMUM ITERATIONS IN CONDITION: stage1' in output:
            print("Error: Exceeded maximum iterations. Terminating process.")
            proc.terminate()  # Terminate the process immediately
            # Run clean-up commands if needed
            run_command("rm *rst")
            run_command("rm *out")
            run_command("clear")
            return  # Exit the function after terminating the process  
    
    proc.wait()
    nice.cancel()
    mean.cancel()

    # Check the return code to determine if the process was terminated
    if proc.returncode is not None and proc.returncode != 0:
        print("Process was terminated due to timeout. Exiting function.")
        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 
        return  # Exit the function if the process was terminated

    # Read text file into database 
    NaOH_Input = pd.read_fwf("magnesitebatch.out")

     # Delete all the NaN columns
    NaOH_Input.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6', 'Column7', 'Column8', 'Column9','Column10', 'Column11']
    NaOH_Input = NaOH_Input.drop(['Column1', 'Column3', 'Column4', 'Column5'], axis = 1)
    NaOH_Input.columns = ['Time(hrs)', 'SiO2(aq)', 'Mg++', 'Gluconic acid(aq)', 'CO2(aq)', 'Na+', 'pH']
    NaOH_Input = NaOH_Input.drop(index = 0)

    NaOH_Input = NaOH_Input.apply(pd.to_numeric, errors='coerce')

    # Obtain the Magnesite Volume Fraction for the NaOHStage Run
    volume2 = pd.read_fwf('volume1.out')

    volume2.columns = ['Column1', 'Column2', 'Column3', 'Column4']
    volume2 = volume2.drop(index = 0)
    volume2 = volume2.drop(index = 1)

    volume2[['Distance','Magnesite']] = volume2.Column2.str.split(expand=True) 

    volume2 = volume2.drop(['Column1', 'Column2', 'Distance'], axis = 1)
    volume2 = volume2.rename(columns={'Column3': 'Quartz'})
    volume2 = volume2.rename(columns={'Column4': 'Amorphous Silica'})

    # Convert all values in the DataFrame to numeric
    volume2 = volume2.apply(pd.to_numeric, errors='coerce')

    run_command("rm *rst")
    run_command("rm *out")
    run_command("clear") 

    NaOH_Input['Time(hrs)'] = NaOH_Input['Time(hrs)'] + 0.1 

    # Stitched Time Series from the Two Input Files 
    combined_Time_Series = pd.concat([Initial_Input, NaOH_Input], ignore_index=True)

    return combined_Time_Series


# Function to Determine Reaction Rate and Carbonation Percent 
def Magnesium_Rate(data, Initial_Seed_Volume):
    # Data here is the combined Time_Series from the Time_Series Function in the format of a pandas dataframe
    # Initial_Seed_Volume is the specified Magnesite Seed that you start with 
    import re 
    import pandas as pd
    import subprocess
    import threading

    # *** you will need to specify path to your crunch executable to run
    # properly!!! ***
    crunch_exe_path = '/Users/tszkipeterwei/Documents/crunchtope/M1MacPre-compiled/CrunchTope-Mac'

    time = data['Time(hrs)']
    mg_concentration = data['Mg++']

    # Algorithm to Find When Equilibrium Occurs 

    threshold = 0.00001  # Threshold for detecting equilibrium
    sustained_period = 3  # Number of consecutive points to check for stability
    significant_change_threshold = 0.0005  # Minimum change to start checking for equilibrium
    found_equilibrium = False  # Track if equilibrium is found
    equilibrium_index = None  # Track the equilibrium index

    # Function to find equilibrium from a given start index and output reaction rate and carbonation percentage 
    def find_equilibrium(start_index):
        equilibrium_indices = []
        for i in range(start_index + 1, len(mg_concentration) - sustained_period + 1):
            stable = True
            for j in range(i, i + sustained_period - 1):
                if abs(mg_concentration[j + 1] - mg_concentration[j]) > threshold:
                    stable = False
                    break
            if stable:
                equilibrium_indices.append(i)
        return equilibrium_indices

    # Find the first significant change in Mg++ concentration
    for start_index in range(1, len(mg_concentration)):
        initial_change = abs(mg_concentration[start_index] - mg_concentration[start_index - 1])
        if initial_change > significant_change_threshold:
            break
    else:
        start_index = None  # If no significant change, start from the beginning

    # Proceed to check for equilibrium only if a significant change was detected
    if start_index is not None:
        equilibrium_found = False

        while not equilibrium_found:
            equilibrium_indices = find_equilibrium(start_index)

            if equilibrium_indices:
                found_equilibrium = True
                equilibrium_index = equilibrium_indices[0]  # Use the first equilibrium initially
                equilibrium_found = True
                
                # Check the rest of the dataset for any new decreases after this equilibrium
                for i in range(equilibrium_index + 1, len(mg_concentration)):
                    if mg_concentration[equilibrium_index] - mg_concentration[i] > significant_change_threshold:
                        # If a new decrease is found, reset the start index and redo the search
                        start_index = i
                        equilibrium_found = False
                        break
            else:
                # If no equilibrium points are found after the start index, exit the loop
                break

    # If equilibrium is found, calculate time and rate up to that point
    if found_equilibrium:
        time_to_equilibrium = time.iloc[equilibrium_index]
        #print('Found Equilibrium')
    else:
        # If no equilibrium is found, use the entire time span
        time_to_equilibrium = time.iloc[-1] 
        #print('No equilibrium')
    
    # This code will put the time of equilibrium in the spatial profile of the input file so that 
    # it could run the input file again, which would allow us to obtain the volume fraction of Magnesite at equilbrium
    # in order to calculate the amount of Mg that got carbonated to get the carbonation percentage 
    if time_to_equilibrium <= 0.1: # If time_equilibrium <= 0.1, run the initialstage.in again with modified spatial profile 
        InitialStage = open("InitialStage.in", "r+") # open the file for read and write mode
        InitialStage.seek(0) # ensure that the file is being read from the top
        data = InitialStage.readlines()

        # Regular expression pattern to match 'spatial_profile' followed by any number
        pattern = r"^spatial_profile\s+([-+]?\d*\.?\d+|\d+)"

        # Iterate through the lines in the file
        for line_number, line in enumerate(data, start=1):
            # Check if the line matches the pattern
            match = re.match(pattern, line.strip())
            if match:
                #print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       {time_to_equilibrium}\n'

        # Close the file when done
        InitialStage.close()

        # Reopen the file to write in the new edit 

        InitialStage = open("InitialStage.in", "w")
    
        InitialStage.writelines(data) # write in the new concentration into the Input File 
    
        InitialStage.close() 

        Pest = open('PestControl.ant', "r+") # open the file for read and write mode
        Pest.seek(0)
        data = Pest.readlines()
        if len(data) > 0:
            data[0] = "InitialStage.in\n"
        else:
            print(f"Error: Not enough lines in the file, current length is {len(data)}")
        
        Pest.close()
        Pest = open('PestControl.ant', "w")
        Pest.writelines(data)
        Pest.close()

       # run the terminal command to execute crunchtope simulation for InitialStage file 
        proc = subprocess.Popen(crunch_exe_path)
        nice = threading.Timer(80, proc.terminate) # if model takes longer than ~1 minutes to run, terminate and move on
        nice.start()
        mean = threading.Timer(130, proc.kill)
        mean.start()
        proc.wait()
        nice.cancel()
        mean.cancel()

        # Check the return code to determine if the process was terminated
        if proc.returncode is not None and proc.returncode != 0:
            print("Process was terminated due to timeout. Exiting function.")
            return  # Exit the function if the process was terminated

        # Obtain the Magnesite Volume Fraction for the InitialStage Run
        volume1 = pd.read_fwf('volume1.out')

        volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4']
        volume1 = volume1.drop(index = 0)
        volume1 = volume1.drop(index = 1)

        volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

        volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
        volume1 = volume1.rename(columns={'Column3': 'Quartz'})
        volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})

        # Convert all values in the DataFrame to numeric
        volume1 = volume1.apply(pd.to_numeric, errors='coerce')

        Magnesite_volume_fraction = volume1['Magnesite'].iloc[0] / 100 # Divide by 100 since volume fraction originally given in percent 

        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 

        # Obtaining the final concentration of Mg in Magnesite (volume fraction * density (g/cm^3) * conversion factor (cm^3 to liters) * molecular weight of Magnesite)
        final_concentration = (Magnesite_volume_fraction - Initial_Seed_Volume) * 3.1 * 1000 * (1/84.31)  # Subtracting the Magnesium concentration from the initial seed 

        # Undo the Changes that you just made
        InitialStage = open("InitialStage.in", "r+") # open the file for read and write mode
        InitialStage.seek(0) # ensure that the file is being read from the top
        data = InitialStage.readlines()

        # Regular expression pattern to match 'spatial_profile' followed by any number
        pattern = r"^spatial_profile\s+([-+]?\d*\.?\d+|\d+)"

        # Iterate through the lines in the file
        for line_number, line in enumerate(data, start=1):
            # Check if the line matches the pattern
            match = re.match(pattern, line.strip())
            if match:
                #print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       0.1\n'

        # Close the file when done
        InitialStage.close()

        # Reopen the file to write in the new edit 

        InitialStage = open("InitialStage.in", "w")
    
        InitialStage.writelines(data) # write in the new concentration into the Input File 
    
        InitialStage.close() 

    elif time_to_equilibrium > 0.1: # Edit the NaOHStage.in file to run spatial profile at the equilibrium time 
        NaOHStage = open("NaOHStage.in", "r+") # open the file for read and write mode
        NaOHStage.seek(0) # ensure that the file is being read from the top
        data = NaOHStage.readlines()

        # Regular expression pattern to match 'spatial_profile' followed by any number
        pattern = r"^spatial_profile\s+([-+]?\d*\.?\d+|\d+)"

        # Iterate through the lines in the file
        for line_number, line in enumerate(data, start=1):
            # Check if the line matches the pattern
            match = re.match(pattern, line.strip())
            if match:
                #print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       {time_to_equilibrium}\n'

        # Close the file when done
        NaOHStage.close()

        # Reopen the file to write in the new edit 

        NaOHStage = open("NaOHStage.in", "w")
    
        NaOHStage.writelines(data) # write in the new concentration into the Input File 
        
        NaOHStage.close() 

        Pest = open('PestControl.ant', "r+") # open the file for read and write mode
        Pest.seek(0)
        data = Pest.readlines()
        if len(data) > 0:
            data[0] = "NaOHStage.in\n"
        else:
            print(f"Error: Not enough lines in the file, current length is {len(data)}")
        
        Pest.close()
        Pest = open('PestControl.ant', "w")
        Pest.writelines(data)
        Pest.close()

        # run the terminal command to execute crunchtope simulation for NaOH file 
        proc = subprocess.Popen(crunch_exe_path)
        nice = threading.Timer(80, proc.terminate) # if model takes longer than ~1 minutes to run, terminate and move on
        nice.start()
        mean = threading.Timer(130, proc.kill)
        mean.start()
        proc.wait()
        nice.cancel()
        mean.cancel()

        # Check the return code to determine if the process was terminated
        if proc.returncode is not None and proc.returncode != 0:
            print("Process was terminated due to timeout. Exiting function.")
            return  # Exit the function if the process was terminated

        # Obtain the Magnesite Volume Fraction for the InitialStage Run
        volume1 = pd.read_fwf('volume1.out')

        volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4']
        volume1 = volume1.drop(index = 0)
        volume1 = volume1.drop(index = 1)

        volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

        volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
        volume1 = volume1.rename(columns={'Column3': 'Quartz'})
        volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})

        # Convert all values in the DataFrame to numeric
        volume1 = volume1.apply(pd.to_numeric, errors='coerce')

        Magnesite_volume_fraction = volume1['Magnesite'].iloc[0] / 100

        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 

        # Obtaining the final concentration of Mg in Magnesite (volume fraction * density (g/cm^3) * conversion factor (liters) * 1/molecular weight of Magnesite)
        final_concentration = (Magnesite_volume_fraction - Initial_Seed_Volume) * 3.1 * 1000 * (1/84.31) # Subtracting the Magnesium concentration from the initial seed 

        # Undo the Changes that you just made
        NaOHStage = open("NaOHStage.in", "r+") # open the file for read and write mode
        NaOHStage.seek(0) # ensure that the file is being read from the top
        data = NaOHStage.readlines()

        # Regular expression pattern to match 'spatial_profile' followed by any number
        pattern = r"^spatial_profile\s+([-+]?\d*\.?\d+|\d+)"

        # Iterate through the lines in the file
        for line_number, line in enumerate(data, start=1):
            # Check if the line matches the pattern
            match = re.match(pattern, line.strip())
            if match:
                #print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       6.0\n'

        # Close the file when done
        NaOHStage.close()

        # Reopen the file to write in the new edit 

        NaOHStage = open("NaOHStage.in", "w")
    
        NaOHStage.writelines(data) # write in the new concentration into the Input File 
        
        NaOHStage.close() 

    # Initial concentration
    initial_concentration = mg_concentration[0] 

    # Calculate the rate of change in concentration
    rate_of_change = (final_concentration) / (time_to_equilibrium - time[0])
    Percent_Carbonation = ((final_concentration)/initial_concentration) * 100 
    # print(f"Initial Concentration: {initial_concentration}")
    # print(f"Final Concentration: {final_concentration}")
    #print(f"Percent Carbonation: {Percent_Carbonation}%")

    #print(f"Time to reach equilibrium or end of experiment: {time_to_equilibrium} hours")
    #print(f"Rate of change in Mg++ concentration: {rate_of_change} mol/kgw per hour")

    return rate_of_change, Percent_Carbonation

# Function to Find the new Temperatures for the Mineral Reaction Rates and Change the Rates in the Input Files 
def Temp(Temp_Input): 
    # Temp_Input is in units of celsius 

    import math
    R = 8.3145 # Ideal Gas Law constant (J/mol *K)
    Temp_ref = 298.15 # Kelvin, reference temp. 

    # This code calculates the reaction rates for mineral precipitation reactions  using the Arrhenius Equation

    # Acid Dependence for Magnesite 
    # Temp_Input is in units of celsius 
    NewTemp = Temp_Input + 273.15 #(Kelvin)

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Acidic Conditions 
    Acid_A = 1.4*10**-4
    # Arrhenius activation energy (J/mol) under Acidic Conditions
    Acid_E = 14.5*10**3

    k_1 = (Acid_A) * math.exp((-Acid_E)/(R*NewTemp))
    Answer1 = math.log10(k_1) 
    Answer1 = round(Answer1, 4)
    Answer1 = str(Answer1)
    # print('Acid depedence log of rate constant for magnesite is ' + Answer1)

    # Carbonate Dependence for Magnesite 
    log_K = -5.22
    activation_energy = 62.7580*10**3 # activation energy in J/mol
    log_K3 = log_K + math.log10(math.exp((-activation_energy/R) * (1/NewTemp - 1/Temp_ref) )) # Calculate log_K2
    log_K3 = round(log_K3, 4)
    log_K3 = str(log_K3)
    # print('Carbonate mechanism log of rate constant for magnesite is ' + log_K3)

    # Neutral Mechanism for Magnesite 

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Neutral Conditions
    Neutral_A = 6.05*10**-6
    # Arrhenius activation energy (J/mol) under Neutral Conditions
    Neutral_E = 23.5*10**3 

    k_2 = (Neutral_A) * math.exp((-Neutral_E)/(R*NewTemp))
    Answer2 = math.log10(k_2) 
    Answer2 = round(Answer2, 4)
    Answer2 = str(Answer2)
    # print('Neutral mechanism log of rate constant for magnesite is ' + Answer2)

    # Neutral Mechanism for Quartz

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Neutral Conditions
    Arrhenius_Quartz = 333
    # Arrhenius activation energy (J/mol) under Neutral Conditions
    Activation_Quartz =  90.9*10**3

    k_4 = (Arrhenius_Quartz) * math.exp((-Activation_Quartz)/(R*NewTemp))
    Answer4 = math.log10(k_4) 
    Answer4 = round(Answer4, 4)
    Answer4 = str(Answer4)
    # print('Neutral mechanism log of rate constant for Quartz is ' + Answer4)

    # Neutral Mechanism for Amorphous Silica 

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Neutral Conditions
    Arrhenius_Silica = 6.65
    # Arrhenius activation energy (J/mol) under Neutral Conditions
    Activation_Silica =  74.5*10**3

    k_5 = (Arrhenius_Silica) * math.exp((-Activation_Silica)/(R*NewTemp))
    Answer5 = math.log10(k_5) 
    Answer5 = round(Answer5, 4)
    Answer5 = str(Answer5)
    # print('Neutral mechanism log of rate constant for Amorphous Silica is ' + Answer5)

    # Correctly opening and reading a file
    try:
        with open("InitialStage.in", "r+") as Initial:
            Initial.seek(0)
            data1 = Initial.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")

    if len(data1) > 43:
        data1[38] = "Magnesite       -label  h+  -rate  " + Answer1 + "\n"
        data1[39] = "Magnesite       -label  carbonate  -rate  " + log_K3 + "\n"
        data1[40] = "Magnesite       -label  neutral  -rate  " + Answer2 + "\n"
        data1[41] = "Quartz          -label  neutral -rate " + Answer4 + "\n"
        data1[42] = "Amorphous_silica  -label neutral -rate " + Answer5 + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Set_Temp = NewTemp - 273.15
    Set_Temp = str(Set_Temp)

    if len(data1) > 106: 
        data1[47] = "temperature      " + Set_Temp + "\n"
        data1[105] = "set_temperature  " + Set_Temp + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Initial.close()
    
    Initial = open("InitialStage.in", "w")

    Initial.writelines(data1)

    Initial.close()

    # Correctly opening and reading a file
    try:
        with open("NaOHStage.in", "r+") as NaOH:
            NaOH.seek(0)
            data1 = NaOH.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")

    if len(data1) > 43:
        data1[38] = "Magnesite       -label  h+  -rate  " + Answer1 + "\n"
        data1[39] = "Magnesite       -label  carbonate  -rate  " + log_K3 + "\n"
        data1[40] = "Magnesite       -label  neutral  -rate  " + Answer2 + "\n"
        data1[41] = "Quartz          -label  neutral -rate " + Answer4 + "\n"
        data1[42] = "Amorphous_silica  -label neutral -rate " + Answer5 + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Set_Temp = NewTemp - 273.15
    Set_Temp = str(Set_Temp)

    if len(data1) > 106: 
        data1[47] = "temperature      " + Set_Temp + "\n"
        data1[105] = "set_temperature  " + Set_Temp + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    NaOH.close()
    
    NaOH = open("NaOHStage.in", "w")

    NaOH.writelines(data1)

    NaOH.close()
    



























