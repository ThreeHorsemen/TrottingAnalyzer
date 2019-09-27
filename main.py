from data_builder import DataBuilder
import pandas as pd

if __name__ == '__main__':

    dataBuilder = DataBuilder()
    lastUpdated = dataBuilder.getLastUpdated()
    print("Database was last updated " + str(lastUpdated[0]) + "." + str(lastUpdated[1]) + "." + str(lastUpdated[2]))
    answer = input("Type 'Y' to update database: ")
    if (answer == "Y"):
        dataBuilder.buildDatabaseFromDate(lastUpdated[0], lastUpdated[1], lastUpdated[2])
        dataBuilder.updateLastUpdated()
        print("Database updated!")

    