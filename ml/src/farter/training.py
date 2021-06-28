import catboost as cb
import pandas as pd
from sklearn.model_selection import train_test_split


# TODO: добавить smoothing factor, чтобы регулировать
#  значимость "do nothing" сэмплов при обучении.
def get_sample_weight(reference_data: pd.Series):
    rows = len(reference_data.index)

    buy_rows = len(reference_data[reference_data > 0])
    sell_rows = len(reference_data[reference_data < 0])
    do_nothing_rows = rows - buy_rows - sell_rows

    buy_rate = (1 - buy_rows / rows) / 2
    sell_rate = (1 - sell_rows / rows) / 2
    do_nothing_rate = (1 - do_nothing_rows / rows) / 2

    return buy_rate, sell_rate, do_nothing_rate


def train_model(indicators_data: pd.DataFrame, reference_data: pd.Series):
    indicators_data = indicators_data.dropna(axis=0)
    reference_data = reference_data.dropna(axis=0)

    indicators_data = indicators_data[indicators_data.index.isin(reference_data.index)]
    reference_data = reference_data[reference_data.index.isin(indicators_data.index)]

    rows = len(indicators_data.index)
    train_size = int(rows * 0.8)

    buy_weight, sell_weight, do_nothing_weight = get_sample_weight(reference_data)

    print(f'buy rate: {buy_weight}, sell rate: {sell_weight}, do nothing rate: {do_nothing_weight}')

    weight = pd.Series(index=reference_data.index, dtype=float)
    weight[reference_data > 0] = buy_weight
    weight[reference_data < 0] = sell_weight
    weight[reference_data == 0] = do_nothing_weight

    classifier = cb.CatBoostClassifier(learning_rate=0.07)
    x_train, x_test, y_train, y_test, w_train, w_test = train_test_split(indicators_data, reference_data, weight,
                                                                         train_size=train_size)
    train_pool = cb.Pool(data=x_train, label=y_train, weight=w_train)
    # Намеренно не используем веса для eval данных,
    # чтобы учитывать "do nothing" сэмплы при подсчете ошибок.
    # TODO: возможно, стоит здесь сделать 'сглаживание' весов
    test_pool = cb.Pool(data=x_test, label=y_test)

    classifier.fit(X=train_pool, eval_set=test_pool)

    return classifier.predict_proba(indicators_data.tail(150))
