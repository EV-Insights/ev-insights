# TODO ottenere la lista delle colonne direttamente dal db
#  ed utilizzarle anche nella creazione delle sql_query
# SELECT *
# FROM sys.columns
# WHERE object_id = OBJECT_ID('TableName')

DATAFRAME_COLUMNS = ['plug_in_datetime',              # When vehicle is plugged-in (timezone-less)
                     'plug_out_datetime',             # When vehicle is plugged-out (timezone-less)
                     'charge_end_datetime',           # When charging session ends (timezone-less)
                     'charge_end_datetime_presence',  # This is true if the real charge_end_datetime is provided, false if it is set to plug_out_datetime
                     'energy_supplied',               # Energy delivered to the EV in kWh
                      'max_charging_power',            # Max charging power set by charger, if any
                     'ev_max_charging_power',         # Max charging power set by EV, if any
                     'ev_id',                         # ID of the EV, if any
                     'charging_station_id',           # ID of the EV charger, if any
                     'user_id',                       # ID of the user, if any
                     ]

CHARGING_POINT_TYPES = ['private (domestic)',
                        'private (workplace)',
                        'public']
