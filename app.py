from textwrap import dedent
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_player as player
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pathlib

FRAMERATE = 24.0

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.config.suppress_callback_exceptions = True

BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

"""Загрузка данных о выбранном футаже - возвращает словарь используемых значений, таких как координаты баундов объектов
    число классов в футаже, матрицу всех классов"""
def load_data(path):
    video_info_df = pd.read_csv(DATA_PATH.joinpath(path))

    # массив классов и число классов
    classes_list = video_info_df["class_str"].value_counts().index.tolist()
    n_classes = len(classes_list)

    # цепляет наименьшее значение требуемое для создания матрицы
    root_round = np.ceil(np.sqrt(len(classes_list)))
    total_size = root_round ** 2
    padding_value = int(total_size - n_classes)
    classes_padded = np.pad(classes_list, (0, padding_value), mode="constant")

    # Все классы внутри матрицы
    classes_matrix = np.reshape(classes_padded, (int(root_round), int(root_round)))
    classes_matrix = np.flip(classes_matrix, axis=0)

    data_dict = {
        "video_info_df": video_info_df,
        "n_classes": n_classes,
        "classes_matrix": classes_matrix,
        "classes_padded": classes_padded,
        "root_round": root_round,
    }

    if True:
        print(f"{path} загружен.")

    return data_dict

# Разметка HTML React
app.layout = html.Div(
    children=[
        html.Div(id="top-bar", className="row"),
        html.Div(
            className="container",
            children=[
                html.Div(
                    id="left-side-column",
                    className="eight columns",
                    children=[
                        html.Img(
                            id="logo-mobile", src=app.get_asset_url("dash-logo.png")
                        ),
                        html.Div(
                            id="header-section",
                            children=[
                                html.H4("Анализ видео - распределение сотрудников на рабочем месте"),
                                html.P(
                                    "Отображение статистики в графике по видиозаписи - непотоковая обработка."
                                    " Координаты обводки лежат в отдельном csv, который генерируется на основе временного ряда."
                                    " Также можно менять отображение на графике в зависимости от порога вероятности."
                                    " Тепловая карта поможет визуализировать частоту появления объектов в кадре даже на длительных видео."
                                ),
                            ],
                        ),
                        html.Div(
                            className="video-outer-container",
                            children=html.Div(
                                className="video-container",
                                children=player.DashPlayer(
                                    id="video-display",
                                    url="https://youtu.be/U1yZ74uRtPQ",
                                    controls=True,
                                    playing=False,
                                    volume=1,
                                    width="100%",
                                    height="100%",
                                ),
                            ),
                        ),
                        html.Div(
                            className="control-section",
                            children=[
                                html.Div(
                                    className="control-element",
                                    children=[
                                        html.Div(
                                            children=["Минимальная вероятность для HeatMap:"]
                                        ),
                                        html.Div(
                                            dcc.Slider(
                                                id="slider-minimum-confidence-threshold",
                                                min=20,
                                                max=80,
                                                marks={
                                                    i: f"{i}%"
                                                    for i in range(20, 81, 10)
                                                },
                                                value=30,
                                                updatemode="drag",
                                            )
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="control-element",
                                    children=[
                                        html.Div(children=["Выбрать видео:"]),
                                        dcc.Dropdown(
                                            id="dropdown-footage-selection",
                                            options=[
                                                {
                                                    "label": "Офис 34 (Корпус 1) - Камера 3",
                                                    "value": "cam3",
                                                },
                                                {
                                                    "label": "Офис 35 (Корпус 1) - Камера 4",
                                                    "value": "cam4",
                                                },
                                                {
                                                    "label": "Офис 36 (Корпус 1) - Камера 5",
                                                    "value": "cam5",
                                                },
                                                {
                                                    "label": "Офис 30 (Общий зал) - Камера 6",
                                                    "value": "cam6",
                                                },
                                                {
                                                    "label": "Выход (Корпус 1) - Камера 7",
                                                    "value": "cam7",
                                                },
                                                {
                                                    "label": "Офис 44 (Переговорная) - Камера 2",
                                                    "value": "cam2",
                                                },
                                            ],
                                            value="cam3",#дефолтное значение
                                            clearable=False,
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="control-element",
                                    children=[
                                        html.Div(children=["Видео:"]),
                                        dcc.Dropdown(
                                            id="dropdown-video-display-mode",
                                            options=[
                                                {
                                                    "label": "Обычное видео",
                                                    "value": "regular",
                                                },
                                                {
                                                    "label": "Видео детекция",
                                                    "value": "bounding_box",
                                                },
                                            ],
                                            value="bounding_box",
                                            searchable=False,
                                            clearable=False,
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="control-element",
                                    children=[
                                        html.Div(children=["Графики:"]),
                                        dcc.Dropdown(
                                            id="dropdown-graph-view-mode",
                                            options=[
                                                {
                                                    "label": "PiePlot и HeatMap",
                                                    "value": "visual",
                                                },
                                                {
                                                    "label": "BarChart",
                                                    "value": "detection",
                                                },
                                            ],
                                            value="visual",
                                            searchable=False,
                                            clearable=False,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="right-side-column",
                    className="four columns",
                    children=[
                        html.Div(
                            className="img-container",
                            children=html.Img(
                                id="logo-web", src=app.get_asset_url("dash-logo.png")
                            ),
                        ),
                        html.Div(id="div-visual-mode"),
                        html.Div(id="div-detection-mode"),
                    ],
                ),
            ],
        ),
    ]
)


# Загрузка данных
@app.server.before_first_request
def load_all_footage():
    global data_dict, url_dict

    # Загружаем словарь csv и названий видео
    data_dict = {
        "cam3": load_data("cam3DetectionData.csv"),
        "cam4": load_data("cam4DetectionData.csv"),
        "cam5": load_data("cam5DetectionData.csv"),
        "cam6": load_data("cam6DetectionData.csv"),
        "cam7": load_data("cam7DetectionData.csv"),
        "cam2": load_data("cam2DetectionData.csv"),
    }

    url_dict = {
        "regular": {
            "cam3": "https://youtu.be/F5EphIxdQ_g",
            "cam4": "https://youtu.be/af7pzMEcmaw",
            "cam5": "https://youtu.be/-jRFSfaXPgk",
            "cam6": "https://youtu.be/rUkbYVRg6qc",
            "cam7": "https://youtu.be/YDN4n-bNWWg",
            "cam2": "https://youtu.be/HP38YWwxa8A",
        },
        "bounding_box": {
            "cam3": "https://youtu.be/U1yZ74uRtPQ",
            "cam4": "https://youtu.be/5ojkd3GFtHI",
            "cam5": "https://youtu.be/hojA1B1sxRU",
            "cam6": "https://youtu.be/C9usZ81dldE",
            "cam7": "https://youtu.be/u5d8WaP_vqw",
            "cam2": "https://youtu.be/pnAobXatpi8",
        },
    }


# Выбор видео
@app.callback(
    Output("video-display", "url"),
    [
        Input("dropdown-footage-selection", "value"),
        Input("dropdown-video-display-mode", "value"),
    ],
)
def select_footage(footage, display_mode):
    # Обновить плеер при смене
    url = url_dict[display_mode][footage]
    return url


@app.callback(
    Output("div-visual-mode", "children"), [Input("dropdown-graph-view-mode", "value")]
)
def update_output(dropdown_value):
    if dropdown_value == "visual":
        return [
            dcc.Interval(id="interval-visual-mode", interval=700, n_intervals=0),
            html.Div(
                children=[
                    html.P(
                        children="Уровень уверенности присутствия объекта",
                        className="plot-title",
                    ),
                    dcc.Graph(id="heatmap-confidence"),
                    html.P(children="Объекты", className="plot-title"),
                    dcc.Graph(id="pie-object-count"),
                ]
            ),
        ]
    return []


@app.callback(
    Output("div-detection-mode", "children"),
    [Input("dropdown-graph-view-mode", "value")],
)
def update_detection_mode(value):
    if value == "detection":
        return [
            dcc.Interval(id="interval-detection-mode", interval=700, n_intervals=0),
            html.Div(
                children=[
                    html.P(
                        children="Уверенность для самых часто встречаемых объектов",
                        className="plot-title",
                    ),
                    dcc.Graph(id="bar-score-graph"),
                ]
            ),
        ]
    return []


# Обновление
@app.callback(
    Output("bar-score-graph", "figure"),
    [Input("interval-detection-mode", "n_intervals")],
    [
        State("video-display", "currentTime"),
        State("dropdown-footage-selection", "value"),
        State("slider-minimum-confidence-threshold", "value"),
    ],
)
def update_score_bar(n, current_time, footage, threshold):
    layout = go.Layout(
        showlegend=False,
        paper_bgcolor="rgb(249,249,249)",
        plot_bgcolor="rgb(249,249,249)",
        xaxis={"automargin": True},
        yaxis={"title": "Score", "automargin": True, "range": [0, 1]},
    )

    if current_time is not None:
        current_frame = round(current_time * FRAMERATE)

        if n > 0 and current_frame > 0:
            video_info_df = data_dict[footage]["video_info_df"]

            # Выбираем подчасть данных под текущий фрейм видео
            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            # Выбираем только фреймы с выбранной порогом вероятности
            threshold_dec = threshold / 100  # Порог
            frame_df = frame_df[frame_df["score"] > threshold_dec]

            # Выбираем до 8 фреймов с высочайшей точностью
            frame_df = frame_df[: min(8, frame_df.shape[0])]
            objects = frame_df["class_str"].tolist()
            object_count_dict = {
                x: 0 for x in set(objects)
            }  # сохранить число объектов
            objects_wc = [] 
            for object in objects:
                object_count_dict[object] += 1
                objects_wc.append(f"{object} {object_count_dict[object]}")

            colors = list("rgb(101,172,91)" for i in range(len(objects_wc)))

            y_text = [
                f"{round(value * 100)}% уверенность"
                for value in frame_df["score"].tolist()
            ]

            figure = go.Figure(
                {
                    "data": [
                        {
                            "hoverinfo": "x+text",
                            "name": "Показатели детекции",
                            "text": y_text,
                            "type": "bar",
                            "x": objects_wc,
                            "marker": {"color": colors},
                            "y": frame_df["score"].tolist(),
                        }
                    ],
                    "layout": {
                        "showlegend": False,
                        "autosize": False,
                        "paper_bgcolor": "rgb(249,249,249)",
                        "plot_bgcolor": "rgb(249,249,249)",
                        "xaxis": {"automargin": True, "tickangle": -45},
                        "yaxis": {
                            "automargin": True,
                            "range": [0, 1],
                            "title": {"text": "Score"},
                        },
                    },
                }
            )
            return figure

    return go.Figure(data=[go.Bar()], layout=layout)  # столбчат график


@app.callback(
    Output("pie-object-count", "figure"),
    [Input("interval-visual-mode", "n_intervals")],
    [
        State("video-display", "currentTime"),
        State("dropdown-footage-selection", "value"),
        State("slider-minimum-confidence-threshold", "value"),
    ],
)
def update_object_count_pie(n, current_time, footage, threshold):
    layout = go.Layout(
        showlegend=True,
        paper_bgcolor="rgb(249,249,249)",
        plot_bgcolor="rgb(249,249,249)",
        autosize=False,
        margin=dict(l=10, r=10, t=15, b=15),
    )

    if current_time is not None:
        current_frame = round(current_time * FRAMERATE)

        if n > 0 and current_frame > 0:
            video_info_df = data_dict[footage]["video_info_df"]

            frame_df = video_info_df[video_info_df["frame"] == current_frame]
            threshold_dec = threshold / 100 
            frame_df = frame_df[frame_df["score"] > threshold_dec]
            class_counts = frame_df["class_str"].value_counts()

            classes = class_counts.index.tolist()
            counts = class_counts.tolist()

            text = [f"{count} detected" for count in counts]

            # Цветовая схема для piechart
            colorscale = [
                "#65ac5b",
                "#74b46b",
                "#83bc7b",
                "#93c48c",
                "#a2cd9c",
                "#b2d5ad",
                "#c1ddbd",
                "#d0e6cd",
                "#e0eede",
                "#ffffff",
            ]

            pie = go.Pie(
                labels=classes,
                values=counts,
                text=text,
                hoverinfo="text+percent",
                textinfo="label+percent",
                marker={"colors": colorscale[: len(classes)]},
            )
            return go.Figure(data=[pie], layout=layout)

    return go.Figure(data=[go.Pie()], layout=layout)  # pie chart


@app.callback(
    Output("heatmap-confidence", "figure"),
    [Input("interval-visual-mode", "n_intervals")],
    [
        State("video-display", "currentTime"),
        State("dropdown-footage-selection", "value"),
        State("slider-minimum-confidence-threshold", "value"),
    ],
)
def update_heatmap_confidence(n, current_time, footage, threshold):
    layout = go.Layout(
        showlegend=False,
        paper_bgcolor="rgb(249,249,249)",
        plot_bgcolor="rgb(249,249,249)",
        autosize=False,
        margin=dict(l=10, r=10, b=20, t=20, pad=4),
    )

    if current_time is not None:
        current_frame = round(current_time * FRAMERATE)

        if n > 0 and current_frame > 0:
            video_info_df = data_dict[footage]["video_info_df"]
            classes_padded = data_dict[footage]["classes_padded"]
            root_round = data_dict[footage]["root_round"]
            classes_matrix = data_dict[footage]["classes_matrix"]

            frame_df = video_info_df[video_info_df["frame"] == current_frame]

            threshold_dec = threshold / 100
            frame_df = frame_df[frame_df["score"] > threshold_dec]

            frame_no_dup = frame_df[["class_str", "score"]].drop_duplicates("class_str")
            frame_no_dup.set_index("class_str", inplace=True)

            score_list = []
            for el in classes_padded:
                if el in frame_no_dup.index.values:
                    score_list.append(frame_no_dup.loc[el][0])
                else:
                    score_list.append(0)

            score_matrix = np.reshape(score_list, (-1, int(root_round)))
            score_matrix = np.flip(score_matrix, axis=0)

            # ставим белый если ничего нет
            if frame_no_dup.shape != (0, 1):
                colorscale = [[0, "#f9f9f9"], [1, "#65ac5b"]]
            else:
                colorscale = [[0, "#f9f9f9"], [1, "#f9f9f9"]]

            hover_text = [f"{score * 100:.2f}% уверенность" for score in score_list]
            hover_text = np.reshape(hover_text, (-1, int(root_round)))
            hover_text = np.flip(hover_text, axis=0)

            classes_matrix = classes_matrix.astype(dtype="|U40")

            for index, row in enumerate(classes_matrix):
                row = list(map(lambda x: "<br>".join(x.split()), row))
                classes_matrix[index] = row

            annotation = []
            for y_cord in range(int(root_round)):
                for x_cord in range(int(root_round)):
                    annotation_dict = dict(
                        showarrow=False,
                        text=classes_matrix[y_cord][x_cord],
                        xref="x",
                        yref="y",
                        x=x_cord,
                        y=y_cord,
                    )
                    if score_matrix[y_cord][x_cord] > 0:
                        annotation_dict["font"] = {"color": "#F9F9F9", "size": "11"}
                    else:
                        annotation_dict["font"] = {"color": "#606060", "size": "11"}
                    annotation.append(annotation_dict)

            # Генерация heatmap

            figure = {
                "data": [
                    {
                        "colorscale": colorscale,
                        "showscale": False,
                        "hoverinfo": "text",
                        "text": hover_text,
                        "type": "heatmap",
                        "zmin": 0,
                        "zmax": 1,
                        "xgap": 1,
                        "ygap": 1,
                        "z": score_matrix,
                    }
                ],
                "layout": {
                    "showlegend": False,
                    "autosize": False,
                    "paper_bgcolor": "rgb(249,249,249)",
                    "plot_bgcolor": "rgb(249,249,249)",
                    "margin": {"l": 10, "r": 10, "b": 20, "t": 20, "pad": 2},
                    "annotations": annotation,
                    "xaxis": {
                        "showticklabels": False,
                        "showgrid": False,
                        "showline": False,
                        "zeroline": False,
                        "side": "top",
                        "ticks": "",
                    },
                    "yaxis": {
                        "showticklabels": False,
                        "showgrid": False,
                        "showline": False,
                        "zeroline": False,
                        "side": "left",
                        "ticks": "",
                    },
                },
            }

            return figure

    # Возвращает пустую фигуру
    return go.Figure(data=[go.Pie()], layout=layout)


# Запуск сервера
if __name__ == "__main__":
    app.run_server(debug=False, port=5001)
