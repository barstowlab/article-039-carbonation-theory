# A Function to Run the Three Input Files InitialStage.in, NaOHStage.in, and CO2Stage.in one after the other
# then the code will save each time series into a dataframe and then piece the three dataframes together to form
# a continuous time series 

# Function to Run Terminal Commands 
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

def Time_Series(PestControl):
    import pandas as pd
    import re
    from openpyxl import load_workbook # import load workbook from openpyxl 
    import matplotlib.pyplot as plt
    # Run the first input file 
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

    # run the terminal command to execute crunchtope simulation for NaOH file 
    command = "Crunchtope-mac"
    run_command(command)

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

    volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5']
    volume1 = volume1.drop(index = 0)
    volume1 = volume1.drop(index = 1)

    volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

    volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
    volume1 = volume1.rename(columns={'Column3': 'Quartz'})
    volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})
    volume1 = volume1.rename(columns={'Column5': 'Forsterite'})

    # Convert all values in the DataFrame to numeric
    volume1 = volume1.apply(pd.to_numeric, errors='coerce')

    Magnesite_volume_fraction = volume1['Magnesite'].iloc[0] / 100
    Quartz_volume_fraction = volume1['Quartz'].iloc[0] / 100
    Amorphous_Silica_volume_fraction = volume1['Amorphous Silica'].iloc[0] / 100
    Forsterite_volume_fraction = volume1['Forsterite'].iloc[0] / 100

    # Delete the output files and clear the terminal 
    run_command("rm *rst")
    run_command("rm *out")
    run_command("clear") 

    # Run the second Input File 

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

    # Define the patterns for each line to modify
    patterns = {
    'Mg++': r"^Mg\+\+\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'SiO2(aq)': r"^SiO2\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'Gluconic_acid(aq)': r"^Gluconic_acid\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?" 
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
                break  # Exit after the first match for this line

    ## Edit the volume fractions in the NaOHstage.in Input File 
    # Define a dictionary to map mineral names to their corresponding regex patterns

    Magnesite_volume_fraction = str(Magnesite_volume_fraction)
    Quartz_volume_fraction = str(Quartz_volume_fraction)
    Amorphous_Silica_volume_fraction = str(Amorphous_Silica_volume_fraction)
    Forsterite_volume_fraction = str(Forsterite_volume_fraction)

    
    # Create a dictionary to hold the volume fractions
    volume_fractions = {
        'Magnesite': Magnesite_volume_fraction,
        'Quartz': Quartz_volume_fraction,
        'Amorphous_Silica': Amorphous_Silica_volume_fraction,
        'Forsterite': Forsterite_volume_fraction
    }

    # Check for zero values and replace them otherwise the Crunchtope Model will not run 
    for mineral, volume in volume_fractions.items():
        if volume in ['0.0', '0', '0.00', '0.000']:
            volume_fractions[mineral] = '1.0e-10'

    # Unpack the updated values back into the original variables
    Magnesite_volume_fraction = volume_fractions['Magnesite']
    Quartz_volume_fraction = volume_fractions['Quartz']
    Amorphous_Silica_volume_fraction = volume_fractions['Amorphous_Silica']
    Forsterite_volume_fraction = volume_fractions['Forsterite']

    patterns = {
        'Magnesite': r"^Magnesite\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Quartz': r"^Quartz\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Amorphous_silica': r"^Amorphous_silica\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Forsterite': r"^Forsterite\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$"
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
            print(f"{mineral} line found at index {index}: {data[index].strip()}")

            # Modify the line with the appropriate volume fraction
            if mineral == 'Magnesite':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Magnesite_volume_fraction, data[index], count=1)
            elif mineral == 'Quartz':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Quartz_volume_fraction, data[index], count=1)
            elif mineral == 'Amorphous_silica':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Amorphous_Silica_volume_fraction, data[index], count=1)
            elif mineral == 'Forsterite':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Forsterite_volume_fraction, data[index], count=1)

            # Update the data at that index with the modified line
            data[index] = modified_line
            print(f"Modified line: {data[index].strip()}")
        
    NaOHStage.close() # close before reopening in writing mode 

    NaOHStage = open("NaOHStage.in", "w")
    
    NaOHStage.writelines(data) # write in the new concentration into the Input File 
    
    NaOHStage.close()

    # run the terminal command to execute crunchtope simulation for NaOH file 
    run_command(command)

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

    volume2.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5']
    volume2 = volume2.drop(index = 0)
    volume2 = volume2.drop(index = 1)

    volume2[['Distance','Magnesite']] = volume2.Column2.str.split(expand=True) 

    volume2 = volume2.drop(['Column1', 'Column2', 'Distance'], axis = 1)
    volume2 = volume2.rename(columns={'Column3': 'Quartz'})
    volume2 = volume2.rename(columns={'Column4': 'Amorphous Silica'})
    volume2 = volume2.rename(columns={'Column5': 'Forsterite'})

    # Convert all values in the DataFrame to numeric
    volume2 = volume2.apply(pd.to_numeric, errors='coerce')

    Magnesite_volume_fraction = volume2['Magnesite'].iloc[0] / 100
    Quartz_volume_fraction = volume2['Quartz'].iloc[0] / 100
    Amorphous_Silica_volume_fraction = volume2['Amorphous Silica'].iloc[0] / 100
    Forsterite_volume_fraction = volume2['Forsterite'].iloc[0] / 100

    run_command("rm *rst")
    run_command("rm *out")
    run_command("clear") 

    # Run the Third Input File 

    Pest = open(PestControl, "r+") # open the file for read and write mode
    Pest.seek(0)
    data = Pest.readlines()
    if len(data) > 0:
        data[0] = "CO2Stage.in\n"
    else:
        print(f"Error: Not enough lines in the file, current length is {len(data)}")
    
    Pest.close()
    Pest = open(PestControl, "w")
    Pest.writelines(data)
    Pest.close()

    # Edit the Initial Primary Species Concentrations in the CO2Stage.in Input File 
    Magnesium_concentration = NaOH_Input['Mg++'].iloc[-1] * 1000 
    SiO2_concentration = NaOH_Input['SiO2(aq)'].iloc[-1] * 1000 
    Gluconic_acid_concentration = NaOH_Input['Gluconic acid(aq)'].iloc[-1] * 1000 
    CO2aq_concentration = NaOH_Input['CO2(aq)'].iloc[-1] * 1000
    Na_concentration = NaOH_Input['Na+'].iloc[-1] * 1000 

    # Edit the Initial pH in the CO2Stage.in Input File 
    pH = NaOH_Input['pH'].iloc[-1]

    # Copy the magnesium concentration from the last entry in the Mg column from NaOH_Input 

    CO2Stage = open("CO2Stage.in", "r+") # open the file for read and write mode
    CO2Stage.seek(0) # ensure that the file is being read from the top
    data = CO2Stage.readlines()

    Magnesium_concentration = str(Magnesium_concentration)
    SiO2_concentration = str(SiO2_concentration)
    CO2aq_concentration = str(CO2aq_concentration)
    Gluconic_acid_concentration = str(Gluconic_acid_concentration)
    Na_concentration = str(Na_concentration)
    pH = str(pH) 

    # Primary Species' Patterns 
    patterns = {
    'Mg++': r"^Mg\+\+\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'SiO2(aq)': r"^SiO2\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'Gluconic_acid(aq)': r"^Gluconic_acid\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'Na+': r"^Na\+\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?",  
    'CO2(aq)': r"^CO2\(aq\)\s+[-+]?\d*\.?\d+([eE][-+]?\d+)?"  
    }

    # Modify the Mg++ line
    for line in data:
        if re.match(patterns['Mg++'], line):
            data[data.index(line)] = f"Mg++             {Magnesium_concentration}\n"
            break  # Exit after modifying the first matching line

    # Modify the SiO2 line
    for line in data:
        if re.match(patterns['SiO2(aq)'], line):
            data[data.index(line)] = f"SiO2(aq)         {SiO2_concentration}\n"
            break  # Exit after modifying the first matching line

    # Modify the Gluconic acid line
    for line in data:
        if re.match(patterns['Gluconic_acid(aq)'], line):
            data[data.index(line)] = f"Gluconic_acid(aq) {Gluconic_acid_concentration}\n"
            break  # Exit after modifying the first matching line

    # Modify the Na+ line
    for line in data:
        if re.match(patterns['Na+'], line):
            data[data.index(line)] = f"Na+              {Na_concentration}\n"
            break  # Exit after modifying the first matching line

    # Modify the CO2 line
    for line in data:
        if re.match(patterns['CO2(aq)'], line):
            data[data.index(line)] = f"CO2(aq)          {CO2aq_concentration}\n"
            break  # Exit after modifying the first matching line

    # Find the index of the first line that starts with 'pH'
    pH_index = next((i for i, line in enumerate(data) if line.startswith('pH')), None)

    if pH_index is None:
        print("No line starting with 'pH' was found.")
        breakpoint() 
    
    data[pH_index] = "pH               "+ pH + "\n" 

    # Convert All Volume Fractions to Strings 
    Magnesite_volume_fraction = str(Magnesite_volume_fraction)
    Quartz_volume_fraction = str(Quartz_volume_fraction)
    Amorphous_Silica_volume_fraction = str(Amorphous_Silica_volume_fraction)
    Forsterite_volume_fraction = str(Forsterite_volume_fraction)

    # Create a dictionary to hold the volume fractions
    volume_fractions = {
        'Magnesite': Magnesite_volume_fraction,
        'Quartz': Quartz_volume_fraction,
        'Amorphous_Silica': Amorphous_Silica_volume_fraction,
        'Forsterite': Forsterite_volume_fraction
    }

    # Check for zero values and replace them otherwise the Crunchtope Model will not run 
    for mineral, volume in volume_fractions.items():
        if volume in ['0.0', '0', '0.00', '0.000']:
            volume_fractions[mineral] = '1.0e-10'

    # Unpack the updated values back into the original variables
    Magnesite_volume_fraction = volume_fractions['Magnesite']
    Quartz_volume_fraction = volume_fractions['Quartz']
    Amorphous_Silica_volume_fraction = volume_fractions['Amorphous_Silica']
    Forsterite_volume_fraction = volume_fractions['Forsterite']

    patterns = {
        'Magnesite': r"^Magnesite\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Quartz': r"^Quartz\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Amorphous_silica': r"^Amorphous_silica\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$",
        'Forsterite': r"^Forsterite\s+[-+]?\d*\.?\d+(e[-+]?\d+)?\s+specific_surface_area\s+\d*\.?\d+$"
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
            print(f"{mineral} line found at index {index}: {data[index].strip()}")

            # Modify the line with the appropriate volume fraction
            if mineral == 'Magnesite':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Magnesite_volume_fraction, data[index], count=1)
            elif mineral == 'Quartz':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Quartz_volume_fraction, data[index], count=1)
            elif mineral == 'Amorphous_silica':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Amorphous_Silica_volume_fraction, data[index], count=1)
            elif mineral == 'Forsterite':
                modified_line = re.sub(r"[-+]?\d*\.?\d+(e[-+]?\d+)?", Forsterite_volume_fraction, data[index], count=1)

            # Update the data at that index with the modified line
            data[index] = modified_line
            print(f"Modified line: {data[index].strip()}")

    CO2Stage.close() # close before reopening in writing mode 

    CO2Stage = open("CO2Stage.in", "w")
    
    CO2Stage.writelines(data) # write in the new concentration into the Input File 
    
    CO2Stage.close()

    # run the terminal command to execute crunchtope simulation for NaOH file 
    run_command(command)

    # Read text file into database 
    CO2_Input = pd.read_fwf("magnesitebatch.out")

     # Delete all the NaN columns
    CO2_Input.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6', 'Column7', 'Column8', 'Column9','Column10', 'Column11']
    CO2_Input = CO2_Input.drop(['Column1', 'Column3', 'Column4', 'Column5'], axis = 1)
    CO2_Input.columns = ['Time(hrs)', 'SiO2(aq)', 'Mg++', 'Gluconic acid(aq)', 'CO2(aq)', 'Na+', 'pH']
    CO2_Input = CO2_Input.drop(index = 0)

    CO2_Input = CO2_Input.apply(pd.to_numeric, errors='coerce')

    # Obtain the Magnesite Volume Fraction for the CO2Stage Run
    volume3 = pd.read_fwf('volume1.out')

    volume3.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6']
    volume3 = volume3.drop(index = 0)
    volume3 = volume3.drop(index = 1)

    volume3[['Distance','Magnesite']] = volume3.Column2.str.split(expand=True) 

    volume3 = volume3.drop(['Column1', 'Column2', 'Distance'], axis = 1)
    volume3 = volume3.rename(columns={'Column3': 'Quartz'})
    volume3 = volume3.rename(columns={'Column4': 'Amorphous Silica'})
    volume3 = volume3.rename(columns={'Column5': 'Fake CO2 Mineral'})
    volume3 = volume3.rename(columns={'Column6': 'Forsterite'})

    # Convert all values in the DataFrame to numeric
    volume3 = volume3.apply(pd.to_numeric, errors='coerce')

    Magnesite_volume_fraction = volume3['Magnesite'].loc[volume3.index[0]]
    Forsterite_volume_fraction = volume3['Forsterite'].loc[volume3.index[0]]

    run_command("rm *rst")
    run_command("rm *out")
    run_command("clear") 

    # Add 0.1 hr to NaOH_Input Dataframe and add 0.2 hr to CO2_Input Dataframe 

    NaOH_Input['Time(hrs)'] = NaOH_Input['Time(hrs)'] + 0.1 
    CO2_Input['Time(hrs)'] = CO2_Input['Time(hrs)'] + 0.2

    # Combine the Dataframes together 

    combined_Time_Series = pd.concat([Initial_Input, NaOH_Input, CO2_Input], ignore_index=True)

    # Plot Mg
    # Assume combined_Time_Series is your DataFrame
    combined_Time_Series['Mg++'] = combined_Time_Series['Mg++'].apply(pd.to_numeric, errors='coerce')

    plt.figure(figsize=(8, 6))
    combined_Time_Series.plot(x='Time(hrs)', y='Mg++')

    plt.xlabel("Time (hrs)")
    plt.ylabel('Concentration (mol/kgw)')

    # Automatically set y-axis limits based on the data
    min_y = combined_Time_Series['Mg++'].min()
    max_y = combined_Time_Series['Mg++'].max()
    plt.ylim(min_y - 0.005, max_y + 0.005)  # Adding a small margin for better visualization

    # Get the y-value (concentration) corresponding to the CO2 bubbling time
    co2_bubble_concentration = combined_Time_Series.loc[combined_Time_Series['Time(hrs)'] == 0.2, 'Mg++'].values[0]

    # Get the y-value (concentration) corresponding to the addition of NaOH 
    NaOH_addition_concentration = combined_Time_Series.loc[combined_Time_Series['Time(hrs)'] == 0.1, 'Mg++'].values[0]

    plt.annotate('NaOH Addition', xy=(0.1, NaOH_addition_concentration), 
                xytext=(0.2, NaOH_addition_concentration + 0.002),
                arrowprops=dict(facecolor='black', arrowstyle='->'))

    plt.annotate('CO2 Bubbling', xy=(0.2, co2_bubble_concentration), 
                xytext=(0.3, co2_bubble_concentration + 0.002),
                arrowprops=dict(facecolor='black', arrowstyle='->'))

    # Ensure that the labels are not cutoff
    plt.tight_layout()

    plt.show()

    # Plot [pH]
    combined_Time_Series['pH'] = combined_Time_Series['pH'].apply(pd.to_numeric, errors='coerce')

    plt.figure(figsize=(8, 6))
    combined_Time_Series.plot(x='Time(hrs)', y='pH')

    plt.xlabel("Time (hrs)")
    plt.ylabel('pH')

    # Get the y-value (pH) corresponding to the CO2 bubbling time
    co2_bubble_concentration = combined_Time_Series.loc[combined_Time_Series['Time(hrs)'] == 0.2, 'pH'].values[0]

    # Get the y-value (pH) corresponding to the addition of NaOH 
    NaOH_addition_concentration = combined_Time_Series.loc[combined_Time_Series['Time(hrs)'] == 0.1, 'pH'].values[0]

    # Define a function to adjust annotation positions dynamically
    def adjust_annotation_position(x, y, offset):
        """Adjust annotation positions based on proximity."""
        # If the y-value is too close to the previous annotation, move it vertically
        return (x + 0.1, y + offset)

    # Adjust offsets dynamically to avoid overlap
    if abs(co2_bubble_concentration - NaOH_addition_concentration) < 0.5:
        # If they are close, stagger the positions
        naoh_offset = 1.5
        co2_offset = -1.5
    else:
        naoh_offset = 1
        co2_offset = 1

    # Apply dynamic adjustment
    naoh_position = adjust_annotation_position(0.1, NaOH_addition_concentration, naoh_offset)
    co2_position = adjust_annotation_position(0.2, co2_bubble_concentration, co2_offset)

    plt.annotate('NaOH Addition', xy=(0.1, NaOH_addition_concentration), 
                xytext=naoh_position,
                arrowprops=dict(facecolor='black', arrowstyle='->'))

    plt.annotate('CO2 Bubbling', xy=(0.2, co2_bubble_concentration), 
                xytext=co2_position,
                arrowprops=dict(facecolor='black', arrowstyle='->'))

    # Ensure that the labels are not cutoff
    plt.tight_layout()

    plt.show()

    return combined_Time_Series, Magnesite_volume_fraction, Forsterite_volume_fraction 

# Function to Determine Reaction Rate and Carbonation Percent 
def Magnesium_Rate(data):
    import matplotlib.pyplot as plt
    import re 
    import pandas as pd
    import numpy as np 
    import seaborn as sns 

    time = data['Time(hrs)']
    mg_concentration = data['Mg++']
    pH = data['pH']

    threshold = 0.00001  # Threshold for detecting equilibrium
    sustained_period = 3  # Number of consecutive points to check for stability
    significant_change_threshold = 0.0005  # Minimum change to start checking for equilibrium
    found_equilibrium = False  # Track if equilibrium is found
    equilibrium_index = None  # Track the equilibrium index

    # Function to find equilibrium from a given start index
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
        final_concentration = mg_concentration.iloc[equilibrium_index]
        print('Found Equilibrium')
    else:
        # If no equilibrium is found, use the entire time span
        time_to_equilibrium = time.iloc[-1] 
        final_concentration = mg_concentration.iloc[-1] 
        print('No equilibrium')
    
    # This code will put the time of equilibrium in the spatial profile of the input file so that 
    # it could the input file can be run again and we can obtain the volume fraction of Magnesite
    # to calculate the amount of Mg that got carbonated to get the carbonation percentage 
    if time_to_equilibrium <= 0.1:
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
                print(f"Pattern found on line {line_number}: {line.strip()}")
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

        # run the terminal command to execute crunchtope simulation for NaOH file 
        command = "Crunchtope-mac"
        run_command(command)

        # Obtain the Magnesite Volume Fraction for the InitialStage Run
        volume1 = pd.read_fwf('volume1.out')

        volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5']
        volume1 = volume1.drop(index = 0)
        volume1 = volume1.drop(index = 1)

        volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

        volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
        volume1 = volume1.rename(columns={'Column3': 'Quartz'})
        volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})
        volume1 = volume1.rename(columns={'Column5': 'Forsterite'})

        # Convert all values in the DataFrame to numeric
        volume1 = volume1.apply(pd.to_numeric, errors='coerce')

        Magnesite_volume_fraction = volume1['Magnesite'].iloc[0] / 100

        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 

        # Obtaining the final concentration of Mg in Magnesite (volume fraction * density (g/cm^3) * conversion factor (liters) * molecular weight of Magnesite)
        final_concentration = Magnesite_volume_fraction * 3.1 * 1000 * (1/84.31) 

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
                print(f"Pattern found on line {line_number}: {line.strip()}")
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

    elif time_to_equilibrium > 0.1 and time_to_equilibrium <= 0.2: 
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
                print(f"Pattern found on line {line_number}: {line.strip()}")
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
        command = "Crunchtope-mac"
        run_command(command)

        # Obtain the Magnesite Volume Fraction for the InitialStage Run
        volume1 = pd.read_fwf('volume1.out')

        volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5']
        volume1 = volume1.drop(index = 0)
        volume1 = volume1.drop(index = 1)

        volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

        volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
        volume1 = volume1.rename(columns={'Column3': 'Quartz'})
        volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})
        volume1 = volume1.rename(columns={'Column5': 'Forsterite'})

        # Convert all values in the DataFrame to numeric
        volume1 = volume1.apply(pd.to_numeric, errors='coerce')

        Magnesite_volume_fraction = volume1['Magnesite'].iloc[0] / 100

        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 

        # Obtaining the final concentration of Mg in Magnesite (volume fraction * density (g/cm^3) * conversion factor (liters) * molecular weight of Magnesite)
        final_concentration = Magnesite_volume_fraction * 3.1 * 1000 * (1/84.31) 

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
                print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       0.1\n'

        # Close the file when done
        NaOHStage.close()

        # Reopen the file to write in the new edit 

        NaOHStage = open("NaOHStage.in", "w")
    
        NaOHStage.writelines(data) # write in the new concentration into the Input File 
        
        NaOHStage.close() 

    elif time_to_equilibrium > 0.2: 
        CO2Stage = open("CO2Stage.in", "r+") # open the file for read and write mode
        CO2Stage.seek(0) # ensure that the file is being read from the top
        data = CO2Stage.readlines()

        # Regular expression pattern to match 'spatial_profile' followed by any number
        pattern = r"^spatial_profile\s+([-+]?\d*\.?\d+|\d+)"

        # Iterate through the lines in the file
        for line_number, line in enumerate(data, start=1):
            # Check if the line matches the pattern
            match = re.match(pattern, line.strip())
            if match:
                print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       {time_to_equilibrium}\n'

        # Close the file when done
        CO2Stage.close()

        # Reopen the file to write in the new edit 

        CO2Stage = open("CO2Stage.in", "w")
    
        CO2Stage.writelines(data) # write in the new concentration into the Input File 
        
        CO2Stage.close() 

        Pest = open('PestControl.ant', "r+") # open the file for read and write mode
        Pest.seek(0)
        data = Pest.readlines()
        if len(data) > 0:
            data[0] = "CO2Stage.in\n"
        else:
            print(f"Error: Not enough lines in the file, current length is {len(data)}")
        
        Pest.close()
        Pest = open('PestControl.ant', "w")
        Pest.writelines(data)
        Pest.close()

        # run the terminal command to execute crunchtope simulation for NaOH file 
        command = "Crunchtope-mac"
        run_command(command)

        # Obtain the Magnesite Volume Fraction for the InitialStage Run
        volume1 = pd.read_fwf('volume1.out')

        volume1.columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6']
        volume1 = volume1.drop(index = 0)
        volume1 = volume1.drop(index = 1)

        volume1[['Distance','Magnesite']] = volume1.Column2.str.split(expand=True) 

        volume1 = volume1.drop(['Column1', 'Column2', 'Distance'], axis = 1)
        volume1 = volume1.rename(columns={'Column3': 'Quartz'})
        volume1 = volume1.rename(columns={'Column4': 'Amorphous Silica'})
        volume1 = volume1.rename(columns={'Column5': 'Fake CO2 Mineral'})
        volume1 = volume1.rename(columns={'Column6': 'Forsterite'})

        # Convert all values in the DataFrame to numeric
        volume1 = volume1.apply(pd.to_numeric, errors='coerce')

        Magnesite_volume_fraction = volume1['Magnesite'].iloc[0] / 100

        run_command("rm *rst")
        run_command("rm *out")
        run_command("clear") 

        # Obtaining the final concentration of Mg in Magnesite (volume fraction * density (g/cm^3) * conversion factor (liters) * molecular weight of Magnesite)
        final_concentration = Magnesite_volume_fraction * 3.1 * 1000 * (1/84.31) 

        # Undo the Change that you just did 
        CO2Stage = open("CO2Stage.in", "r+") # open the file for read and write mode
        CO2Stage.seek(0) # ensure that the file is being read from the top
        data = CO2Stage.readlines()

        # Regular expression pattern to match 'spatial_profile' followed by any number
        pattern = r"^spatial_profile\s+([-+]?\d*\.?\d+|\d+)"

        # Iterate through the lines in the file
        for line_number, line in enumerate(data, start=1):
            # Check if the line matches the pattern
            match = re.match(pattern, line.strip())
            if match:
                print(f"Pattern found on line {line_number}: {line.strip()}")
                break
        else:
            print("Pattern not found in the file.")

        data[line_number - 1] = f'spatial_profile       6.0\n'

        # Close the file when done
        CO2Stage.close()

        # Reopen the file to write in the new edit 

        CO2Stage = open("CO2Stage.in", "w")
    
        CO2Stage.writelines(data) # write in the new concentration into the Input File 
        
        CO2Stage.close() 

    # Initial concentration
    initial_concentration = mg_concentration[0] + 142.16/1000 # Adding the Magnesium concentration from Forsterite 

    # Calculate the rate of change in concentration
    rate_of_change = (final_concentration) / (time_to_equilibrium - time[0])
    Percent_Carbonation = ((final_concentration)/initial_concentration) * 100 
    print(f"Initial Concentration: {initial_concentration}")
    print(f"Final Concentration: {final_concentration}")
    print(f"Percent Carbonation: {Percent_Carbonation}%")

    print(f"Time to reach equilibrium or end of experiment: {time_to_equilibrium} hours")
    print(f"Rate of change in Mg++ concentration: {rate_of_change} mol/kgw per hour")

    # Get the Magnesite Concentration
    Magnesite_Concentration = []

    for i in range(len(time)):
        if time[i] < 0.1:
            # For indices where time < 0.1, set Magnesite Concentration to 0
            Magnesite_Concentration.append(0)
        else:
            # After time >= 0.1, calculate Magnesite Concentration
            if i == 0:
                MgCO3 = 0  # Ensure the first value is 0 (if applicable)
            else:
                MgCO3 = (mg_concentration[i-1] - mg_concentration[i]) + Magnesite_Concentration[i-1]
            Magnesite_Concentration.append(MgCO3)

    # Graph the Mg++, MgCO3, and pH 

    # Set Seaborn style
    sns.set_theme(style="ticks")
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['svg.fonttype'] = 'none'  # Ensure fonts are preserved as text in SVG

    # Create a dual-axis plot
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Set the background color of the plot area to white
    ax1.set_facecolor("white")

    # Plot Mg++ and MgCO₃ concentrations on the first y-axis
    line1, = ax1.plot(time, mg_concentration, color="blue", label="Mg++")
    line2, = ax1.plot(time, Magnesite_Concentration, color="green", label="MgCO3")

    # Customize first y-axis
    ax1.set_xlabel("Time (hr)", color="black")
    ax1.set_ylabel("Concentration (M)", color="black")
    ax1.tick_params(axis="y", labelcolor="black")
    ax1.tick_params(axis="x", direction="out", length=8, color="black", width = 1.5)
    ax1.set_xlim(0, 6.2)

    # Create second y-axis for pH
    ax2 = ax1.twinx()
    line3, = ax2.plot(time, pH, color="red", label="pH")

    # Customize second y-axis for pH
    ax2.set_ylabel("pH", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax2.set_ylim(0, 12)
    ax2.set_yticks(range(0, 13, 2))


    # Adjust spines to create a black border
    for spine in ax1.spines.values():
        spine.set_edgecolor("black")
        spine.set_linewidth(1.5)

    ax2.spines["right"].set_edgecolor("black")
    ax2.spines["right"].set_linewidth(1.5)
    ax2.spines["left"].set_edgecolor("black")
    ax2.spines["bottom"].set_edgecolor("none")
    ax2.spines["top"].set_edgecolor("black")
    

    # Set all spines for ax1 to black
    ax1.spines["left"].set_edgecolor("black")
    ax1.spines["top"].set_edgecolor("black")

    # Adjust their linewidth as needed
    ax1.spines["left"].set_linewidth(1.5)
    ax1.spines["top"].set_linewidth(1.5)

    ax1.spines['bottom'].set_visible(True)
    ax1.spines['bottom'].set_edgecolor("black")  # Set to black for consistency
    ax1.spines["bottom"].set_linewidth(1.5)


    # Add a black border around the entire figure
    fig.patch.set_edgecolor("black")
    fig.patch.set_linewidth(1.5)

    # Ensure tick marks are drawn above the grid
    ax1.tick_params(axis="y", zorder=2)
    ax1.tick_params(axis="x", zorder=2)

    # Create the vertical line and store its handle
    vertical_line = plt.axvline(x=0.2, ymin=0, ymax=1, color='black', linestyle='--', linewidth=1, label='CO2 Bubbling')
    vertical_line2 = plt.axvline(x=0.1, ymin=0, ymax=1, color='black', linestyle=':', linewidth=1, label='NaOH Addition')
    vertical_line3 = plt.axvline(x=time_to_equilibrium, ymin=0, ymax=1, color='black', linestyle='-', linewidth=1, label='Equilibrium Point')

    # Combine legends
    lines = [line1, line2, line3, vertical_line2, vertical_line, vertical_line3]  # Add the vertical line to the list
    labels = [line.get_label() for line in lines]
    fig.legend(lines, labels, loc="upper right", bbox_to_anchor=(1.18, 0.93), title="Legend", facecolor="white")


    # Fix layout to ensure the figure border is not cropped
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave extra space for elements

    # Show plot
    plt.show()

    # Save file as SVG; change file name for different runs
    #fig.savefig("Figure SVG/Olivine Model at 100°C.svg", bbox_inches="tight", edgecolor="black", format="svg")

    return rate_of_change, Percent_Carbonation

# Function to Find the new Temperatures for the Mineral Reaction Rates 
def Temp(Temp_Input): 

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
    print('Acid depedence log of rate constant for magnesite is ' + Answer1)

    # Carbonate Dependence for Magnesite 
    log_K = -5.22
    activation_energy = 62.7580*10**3 # activation energy in J/mol
    log_K3 = log_K + math.log10(math.exp((-activation_energy/R) * (1/NewTemp - 1/Temp_ref) )) # Calculate log_K2
    log_K3 = round(log_K3, 4)
    log_K3 = str(log_K3)
    print('Carbonate mechanism log of rate constant for magnesite is ' + log_K3)

    # Neutral Mechanism for Magnesite 

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Neutral Conditions
    Neutral_A = 6.05*10**-6
    # Arrhenius activation energy (J/mol) under Neutral Conditions
    Neutral_E = 23.5*10**3 

    k_2 = (Neutral_A) * math.exp((-Neutral_E)/(R*NewTemp))
    Answer2 = math.log10(k_2) 
    Answer2 = round(Answer2, 4)
    Answer2 = str(Answer2)
    print('Neutral mechanism log of rate constant for magnesite is ' + Answer2)

    # Neutral Mechanism for Quartz

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Neutral Conditions
    Arrhenius_Quartz = 333
    # Arrhenius activation energy (J/mol) under Neutral Conditions
    Activation_Quartz =  90.9*10**3

    k_4 = (Arrhenius_Quartz) * math.exp((-Activation_Quartz)/(R*NewTemp))
    Answer4 = math.log10(k_4) 
    Answer4 = round(Answer4, 4)
    Answer4 = str(Answer4)
    print('Neutral mechanism log of rate constant for Quartz is ' + Answer4)

    # Neutral Mechanism for Amorphous Silica 

    # Arrhenius pre-exponetial factor A, mole * m^-2 * s^-1 under Neutral Conditions
    Arrhenius_Silica = 6.65
    # Arrhenius activation energy (J/mol) under Neutral Conditions
    Activation_Silica =  74.5*10**3

    k_5 = (Arrhenius_Silica) * math.exp((-Activation_Silica)/(R*NewTemp))
    Answer5 = math.log10(k_5) 
    Answer5 = round(Answer5, 4)
    Answer5 = str(Answer5)
    print('Neutral mechanism log of rate constant for Amorphous Silica is ' + Answer5)

    # Acid Mechanism for Forsterite 
    log_K1 = -6.85
    Acid_Forsterite_Energy = 67.2*10**3 # Units: J/mol 

    Answer6 = log_K1 + math.log10(math.exp((-Acid_Forsterite_Energy/R) * (1/NewTemp - 1/Temp_ref) )) # Calculate log_K2
    Answer6 = round(Answer6, 4)
    Answer6 = str(Answer6)
    print('Acid mechanism log of rate constant for forsterite is ' + Answer6)

    # Neutral Mechanism for Forsterite 
    log_K2 = -10.64
    Neutral_Forsterite_Energy = 79.0*10**3 # Units: J/mol 

    Answer7 = log_K2 + math.log10(math.exp((-Neutral_Forsterite_Energy/R) * (1/NewTemp - 1/Temp_ref) )) # Calculate log_K2
    Answer7 = round(Answer7, 4)
    Answer7 = str(Answer7)
    print('Neutral mechanism log of rate constant for forsterite is ' + Answer7)

    # Correctly opening and reading a file
    try:
        with open("InitialStage.in", "r+") as Initial:
            Initial.seek(0)
            data1 = Initial.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")

    if len(data1) > 45:
        data1[38] = "Magnesite       -label  h+  -rate  " + Answer1 + "\n"
        data1[39] = "Magnesite       -label  carbonate  -rate  " + log_K3 + "\n"
        data1[40] = "Magnesite       -label  neutral  -rate  " + Answer2 + "\n"
        data1[41] = "Quartz          -label  neutral -rate " + Answer4 + "\n"
        data1[42] = "Amorphous_silica  -label neutral -rate " + Answer5 + "\n"
        data1[43] = "Forsterite     -label  h+  -rate " + Answer6 + "\n"
        data1[44] = "Forsterite     -label  neutral  -rate " + Answer7 + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Set_Temp = NewTemp - 273.15
    Set_Temp = str(Set_Temp)

    if len(data1) > 109: 
        data1[49] = "temperature      " + Set_Temp + "\n"
        data1[108] = "set_temperature  " + Set_Temp + "\n"
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

    if len(data1) > 45:
        data1[38] = "Magnesite       -label  h+  -rate  " + Answer1 + "\n"
        data1[39] = "Magnesite       -label  carbonate  -rate  " + log_K3 + "\n"
        data1[40] = "Magnesite       -label  neutral  -rate  " + Answer2 + "\n"
        data1[41] = "Quartz          -label  neutral -rate " + Answer4 + "\n"
        data1[42] = "Amorphous_silica  -label neutral -rate " + Answer5 + "\n"
        data1[43] = "Forsterite     -label h+ -rate " + Answer6 + "\n"
        data1[44] = "Forsterite     -label neutral -rate " + Answer7 + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Set_Temp = NewTemp - 273.15
    Set_Temp = str(Set_Temp)

    if len(data1) > 109: 
        data1[49] = "temperature      " + Set_Temp + "\n"
        data1[108] = "set_temperature  " + Set_Temp + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    NaOH.close()
    
    NaOH = open("NaOHStage.in", "w")

    NaOH.writelines(data1)

    NaOH.close()

    # Correctly opening and reading a file
    try:
        with open("CO2Stage.in", "r+") as Final:
            Final.seek(0)
            data1 = Final.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")

    if len(data1) > 45:
        data1[37] = "Magnesite       -label  h+  -rate  " + Answer1 + "\n"
        data1[38] = "Magnesite       -label  carbonate  -rate  " + log_K3 + "\n"
        data1[39] = "Magnesite       -label  neutral  -rate  " + Answer2 + "\n"
        data1[40] = "Quartz          -label  neutral -rate " + Answer4 + "\n"
        data1[41] = "Amorphous_silica  -label neutral -rate " + Answer5 + "\n"
        data1[43] = "Forsterite     -label h+ -rate " + Answer6 + "\n"
        data1[44] = "Forsterite     -label neutral -rate " + Answer7 + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Set_Temp = NewTemp - 273.15
    Set_Temp = str(Set_Temp)

    if len(data1) > 110: 
        data1[49] = "temperature      " + Set_Temp + "\n"
        data1[109] = "set_temperature  " + Set_Temp + "\n"
    # else:
    #     print(f"Error: Not enough lines in the file, current length is {len(data1)}")
    #     breakpoint()

    Final.close()
    
    Final = open("CO2Stage.in", "w")

    Final.writelines(data1)

    Final.close()


def plot_bar_graph(file_path, y_label='Y Variable'):
    import matplotlib.pyplot as plt
    import seaborn as sns 
    import pandas as pd
    # Load the CSV file
    data = pd.read_csv(file_path)

    # Set figure size to allow space for labels
    plt.figure(figsize=(8, 6))  # Adjust dimensions as needed

    # Create the bar chart with Seaborn
    sns.set_theme(style="ticks")
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams['svg.fonttype'] = 'none'  # Ensure fonts are preserved as text in SVG
    ax = sns.barplot(x='Temperature (°C)', y=data.columns[1], data=data, palette="viridis")

    # Labeling
    ax.set_xlabel('Temperature (°C)', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.tick_params(axis='both', labelsize=10)

    # Set y-axis limits dynamically
    max_value = data[data.columns[1]].max()
    min_value = data[data.columns[1]].min()

    if abs(max_value) > abs(min_value):
        ymax = max_value * 1.1
    else:
        ymax = min_value * 1.1

    if ymax < 0:
        ax.set_ylim(0, -1 * ymax)
    elif ymax == 0:
        ax.set_ylim(0, ymax + 1)
    elif ymax > 0:
        ax.set_ylim(0, ymax)

    # Adjust layout for better spacing
    plt.tight_layout(pad=2.0)  # Add padding for labels

    # Save file as SVG; change file name for different runs
    #plt.savefig("Figure SVG/Olivine Model Forsterite Fraction.svg", bbox_inches="tight", edgecolor="black", format="svg")

    plt.show()


























