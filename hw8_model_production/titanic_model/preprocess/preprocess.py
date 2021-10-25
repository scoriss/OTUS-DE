import pandas as pd
from sklearn.preprocessing import LabelEncoder

def preprocess_data(model_data: pd.DataFrame) -> pd.DataFrame:

    # Set Age groups
    model_data['Age_Range'] = pd.cut(model_data.Age, [0, 10, 20, 30, 40, 50, 60, 70, 80])

    # Set Parch classifiers
    model_data['Family'] = model_data.Parch + model_data.SibSp
    model_data['Is_Alone'] = model_data.Family == 0

    # Set Fare Category
    model_data['Fare_Category'] = pd.cut(model_data['Fare'], bins=[0, 7.90, 14.45, 31.28, 120],
                                labels=['Low', 'Mid', 'High_Mid', 'High'])

    # Set Embarked to Southampton Since embarked only has two missing values and the highest number of people boarded the
    # ship from Southampton, the probablity of boarding from Southampton is high. So, we fill the missing values with
    # Southampton. However, instead of manually putting in Southampton, we would find the mode of the Embarked column and
    # substitute missing values with it.
    model_data.Embarked.fillna(model_data.Embarked.mode()[0], inplace=True)

    model_data['Salutation'] = model_data.Name.apply(lambda name: name.split(',')[1].split('.')[0].strip())

    grp = model_data.groupby(['Sex', 'Pclass'])
    model_data.Age = grp.Age.apply(lambda x: x.fillna(x.median()))

    # If still any row remains
    model_data.Age.fillna(model_data.Age.median, inplace=True)

    # Assigning NA for non available cabin values. Pulling deck value from Cabin and adding a feature 'Deck'
    model_data.Cabin = model_data.Cabin.fillna('NA')

    # Using Pandas' get dummies we encoded the categorical data. Later, we drop all the columns we encoded.
    model_data = pd.concat([model_data, pd.get_dummies(model_data.Cabin, prefix="Cabin"),
                    pd.get_dummies(model_data.Age_Range, prefix="Age_Range"),
                    pd.get_dummies(model_data.Embarked, prefix="Emb", drop_first=True),
                    pd.get_dummies(model_data.Salutation, prefix="Title", drop_first=True),
                    pd.get_dummies(model_data.Fare_Category, prefix="Fare", drop_first=True),
                    pd.get_dummies(model_data.Pclass, prefix="Class", drop_first=True)], axis=1)
    model_data['Sex'] = LabelEncoder().fit_transform(model_data['Sex'])
    model_data['Is_Alone'] = LabelEncoder().fit_transform(model_data['Is_Alone'])

    model_data.drop(['Pclass', 'Fare', 'Cabin', 'Fare_Category', 'Name', 'Salutation', 'Ticket', 'Embarked', 'Age_Range', 'SibSp',
            'Parch', 'Age'], axis=1, inplace=True)

    return model_data