# Load Data
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
import pickle

def load_column_array(cols):
    cols_booleans = [
        "IsBeta",
        "IsSxsPassiveMode",
        "HasTpm",
        "IsProtected",
        "AutoSampleOptIn",
        "PuaMode",
        "SMode",
        "Firewall",
        "UacLuaenable",
        "Census_HasOpticalDiskDrive",
        "Census_IsPortableOperatingSystem",
        "Census_IsFlightingInternal",
        "Census_IsFlightsDisabled",
        "Census_ThresholdOptIn",
        "Census_IsSecureBootEnabled",
        "Census_IsWIMBootEnabled",
        "Census_IsVirtualDevice",
        "Census_IsTouchEnabled",
        "Census_IsPenCapable",
        "Census_IsAlwaysOnAlwaysConnectedCapable",
        "Wdft_IsGamer"
    ]

    cols_categorical = [
        "ProductName",
        "EngineVersion",
        "AppVersion",
        "AvSigVersion_x_x",
        "RtpStateBitfield",
        "AVProductsInstalled",
        "AVProductsEnabled",
        "CountryIdentifier",
        "OrganizationIdentifier",
        "Platform",
        "Processor",
        "OsVer",
        "OsBuild",
        "OsSuite",
        "OsPlatformSubRelease",
        "SkuEdition",
        "SmartScreen",
        "Census_MDC2FormFactor",
        "Census_DeviceFamily",
        "Census_ProcessorManufacturerIdentifier",
        "Census_ProcessorClass",
        "Census_PrimaryDiskTypeName",
        "Census_ChassisTypeName",
        "Census_PowerPlatformRoleName",
        "Census_InternalBatteryType",
        "Census_OSArchitecture",
        "Census_OSBranch",
        "Census_OSBuildNumber",
        "Census_OSEdition",
        "Census_OSSkuName",
        "Census_OSInstallTypeName",
        "Census_OSInstallLanguageIdentifier",
        "Census_OSUILocaleIdentifier",
        "Census_OSWUAutoUpdateOptionsName",
        "Census_GenuineStateName",
        "Census_ActivationChannel",
        "Census_FlightRing",
        "Wdft_RegionIdentifier"
    ]

    cols_categorical_large = [
        "AvSigVersion",
        "DefaultBrowsersIdentifier",
        "AVProductStatesIdentifier",
        "CityIdentifier",
        "GeoNameIdentifier",
        "OsBuildLab",
        "IeVerIdentifier",
        "Census_OEMNameIdentifier",
        "Census_OEMModelIdentifier",
        "Census_ProcessorModelIdentifier",
        "Census_OSVersion",
        "Census_OSBuildRevision",
        "Census_FirmwareManufacturerIdentifier",
        "Census_FirmwareVersionIdentifier",
        "LocaleEnglishNameIdentifier"
    ]

    cols_numerical = [
        "Census_ProcessorCoreCount",
        "Census_PrimaryDiskTotalCapacity",
        "Census_SystemVolumeTotalCapacity",
        "Census_TotalPhysicalRAM",
        "Census_InternalPrimaryDiagonalDisplaySizeInInches",
        "Census_InternalPrimaryDisplayResolutionHorizontal",
        "Census_InternalPrimaryDisplayResolutionVertical",
        "Census_InternalBatteryNumberOfCharges"
    ]
    
    # Update our column arrays
    cols_categorical = [x for x in cols_categorical if x in cols]
    cols_numerical = [x for x in cols_numerical if x in cols]
    cols_booleans = [x for x in cols_booleans if x in cols]
    cols_categorical_large = [x for x in cols_categorical_large if x in cols]
    
    return cols_categorical, cols_numerical, cols_booleans, cols_categorical_large

def get_one_hot_encodings(df, cols):
    result = pd.DataFrame()
    i = 0
    for col in cols:
        dummies = pd.get_dummies(df[col],prefix=col)
        if( i == 0 ):
            result = dummies.copy()
        else:
            result = pd.concat((result, dummies), axis=1)
        i+=1
    return result

def reduce_features(df, verbose = False):
    # calculate the correlation matrix
    corr_matrix  = df.corr().abs()

    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))

    # Find index of feature columns with correlation greater than 0.95
    to_drop = [column for column in upper.columns if any(upper[column] > 0.95)]
    
    #Get all of the correlation values > 95%
    x = np.where(upper > 0.95)

    #Display all field combinations with > 95% correlation
    cf = pd.DataFrame()
    cf['Field1'] = upper.columns[x[1]]
    cf['Field2'] = upper.index[x[0]]

    #Get the correlation values for every field combination. (There must be a more pythonic way to do this!)
    corr = [0] * len(cf)
    for i in range(0, len(cf)):
        corr[i] =  upper[cf['Field1'][i]][cf['Field2'][i]] 

    cf['Correlation'] = corr

    if( verbose ):
        print('There are ', str(len(cf['Field1'])), ' field correlations > 95%.')
        display(cf)
        
        print('Dropping the following ', str(len(to_drop)), ' highly correlated fields.')
        to_drop
        
    #Check columns before drop 
    if( verbose ):
        print('\r\n*********Before: Dropping Highly Correlated Fields*************************************')
        display(df.info(verbose=False))

    # Drop the highly correlated features from our training data 
    df = df.drop(to_drop, axis=1)

    #Check columns after drop 
    if( verbose ):
        print('\r\n*********After: Dropping Highly Correlated Fields**************************************')
        df.info(verbose=False)
    
    return df

# Get data and create a model
subMalware = pd.read_csv("data/malware.subsample.csv")
cols_categorical, cols_numerical, cols_booleans, cols_categorical_large = load_column_array(subMalware.columns)
subMalware[cols_categorical] = subMalware[cols_categorical].astype(object)
subMalware[cols_categorical_large] = subMalware[cols_categorical_large].astype(object)

HasDetections_model_data = pd.concat(
    (    
        subMalware[cols_booleans],
        subMalware[cols_numerical],
        get_one_hot_encodings(subMalware, cols_categorical)
    ), axis = 1)

HasDetections_response_data = subMalware["HasDetections"]

HasDetections_model_data = reduce_features(HasDetections_model_data, verbose=False)


X = HasDetections_model_data.values
y = HasDetections_response_data.values

# Creat eth Cross Validation Objected used for all tests
num_cv_iterations = 10
random_st = 42
kfold_cv = KFold(
    n_splits=num_cv_iterations,
    random_state = random_st
)

clf = RandomForestClassifier(random_state=42)

grid_params = [{
    "max_features" : ["auto","log2",0.20, 0.30],
    "n_estimators" : [10,50,100],
    "min_samples_leaf" : [25, 50, 100]
}]

scoring = {
    'acc':'accuracy',
    'precision':'precision',
    'recall':'recall',
    'auc':'roc_auc',
    'mse':'neg_mean_squared_error',
    'r2':'r2'
}

grid_clf = GridSearchCV(
    estimator = clf, 
    param_grid=grid_params, 
    cv=kfold_cv, 
    scoring=scoring,
    refit='auc',
    n_jobs=-2,verbose=1,return_train_score=False)
grid_clf.fit(X, y)

# Save Model
filename = 'models/HasDetections_GridSearch_RF_final.pkl'
pickle.dump(grid_clf, open(filename, 'wb'))