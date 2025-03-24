# This Python Function will Calculate the log K of dissolution for CO2min based on the partial pressure of 
# CO2 being bubbled in and then modify the database entry of CO2min accordingly 

def CO2min_logKeq(partial_pressure):
    import math

    partial_pressure = float(partial_pressure) # partial pressure should be in units of bar 

    # Henry's Constant for CO2 in water at 25 degrees Celsius 

    Href = 0.034 # Units of mol/ (kgw*bar) From NIST 

    # Temperatures (in units of Kelvin)
    Temp_ref = 298.15 # Reference temperature at 25 degrees Celsius
    Temp_0 = 273.15 # Temperature at 0 degrees Celsius 
    Temp_60 = 333.15 # Temperature at 60 degrees Celsius 
    Temp_100 = 373.15 # Temperature at 100 degrees Celsius 
    Temp_150 = 423.15 # Temperature at 150 degrees Celsius 
    Temp_200 = 473.15 # Temperature at 200 degrees Celsius 
    Temp_250 = 523.15 # Temperature at 250 degrees Celsius 
    Temp_300 = 573.15 # Temperature at 300 degrees Celsius 

    H_0 = Href*math.exp(2400 * (1/Temp_0 - 1/Temp_ref)) # Calculate H at 0 degrees Celsius
    H_25 = Href 
    H_60 = Href*math.exp(2400 * (1/Temp_60 - 1/Temp_ref)) 
    H_100 = Href*math.exp(2400 * (1/Temp_100 - 1/Temp_ref)) 
    H_150 = Href*math.exp(2400 * (1/Temp_150 - 1/Temp_ref)) 
    H_200 = Href*math.exp(2400 * (1/Temp_200 - 1/Temp_ref)) 
    H_250 = Href*math.exp(2400 * (1/Temp_250 - 1/Temp_ref)) 
    H_300 = Href*math.exp(2400 * (1/Temp_300 - 1/Temp_ref)) 

    # Calculate the log10 K values for CO2min 
    Log_Keq_0 = round(math.log10(H_0 * partial_pressure), 4)
    Log_Keq_25 = round(math.log10(H_25 * partial_pressure), 4) 
    Log_Keq_60 = round(math.log10(H_60 * partial_pressure), 4)
    Log_Keq_100 = round(math.log10(H_100 * partial_pressure), 4)
    Log_Keq_150 = round(math.log10(H_150 * partial_pressure), 4) 
    Log_Keq_200 = round(math.log10(H_200 * partial_pressure), 4)
    Log_Keq_250 = round(math.log10(H_250 * partial_pressure), 4)
    Log_Keq_300 = round(math.log10(H_300 * partial_pressure), 4)  

    Log_Keq_0 = str(Log_Keq_0)
    Log_Keq_25 = str(Log_Keq_25)
    Log_Keq_60 = str(Log_Keq_60)
    Log_Keq_100 = str(Log_Keq_100)
    Log_Keq_150 = str(Log_Keq_150)
    Log_Keq_200 = str(Log_Keq_200)
    Log_Keq_250 = str(Log_Keq_250)
    Log_Keq_300 = str(Log_Keq_300)

    # Edit the CO2min Database Line in the OldRifleDatabaseLiLi.dbs 

    Database = open('OldRifleDatabaseLiLi.dbs', "r+")
    Database.seek(0)
    CO2_Entry = Database.readlines()
    if len(CO2_Entry) > 2083:
        CO2_Entry[2083] = "'CO2min'   36.9340  1   1.0000 'CO2(aq)'   "+ Log_Keq_0 + "     "+ Log_Keq_25 +"     "+ Log_Keq_60 +"     "+ Log_Keq_100 +"     "+ Log_Keq_150 +"     " + Log_Keq_200+"     "+Log_Keq_250 +"     " + Log_Keq_300+ "   44.01 \n"
    else:
        print(f"Error: Not enough lines in the file, current length is {len(CO2_Entry)}")
    
    Database.close()

    print(CO2_Entry[2083])

    Database = open("OldRifleDatabaseLiLi.dbs", "w")

    Database.writelines(CO2_Entry)

    Database.close() 









