import plotly.graph_objects as go
import pandas as pd
import numpy as np

def get_chart_types():
    return {
        "Line Chart": "line"
    }

def get_sentiment_emoji(sentiment):
    emoji_map = {
        'anxious': '😰',
        'confident': '😊',
        'disappointed': '😞',
        'excited': '😃',
        'indifferent': '😐',
        'optimistic': '😀',
        'uncertain': '🤔',
        'worried': '😟'
    }
    return emoji_map.get(sentiment, '❓')

def display_stock_chart(data, chart_type='line', ticker='', is_forecast=False):
    layout = go.Layout(
        title=f"{ticker} {'Forecast' if is_forecast else 'Historical'} Prices",
        xaxis={'title': 'Date'},
        yaxis={'title': 'Price'},
        hovermode='closest',
        height=500
    )
    
    fig = go.Figure(layout=layout)
    
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['close'],
            mode='lines',
            name='Price',
            line=dict(color='blue', width=2),
            hovertemplate='%{x}<br>Price: $%{y:.2f}<extra></extra>'
        )
    )
    
    if not is_forecast and 'emo_label' in data.columns:
        emojis = [get_sentiment_emoji(sentiment) for sentiment in data['emo_label']]
        sentiments = data['emo_label'].tolist()
        
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data['close'],
                mode='markers',
                marker=dict(
                    size=12,
                    color='rgba(0, 0, 0, 0)',
                    symbol='circle',
                    line=dict(width=0)
                ),
                hoverinfo='x+y+text',
                name='Click for Sentiment',
                text=[f"{emoji} {sentiment}" for emoji, sentiment in zip(emojis, sentiments)],
                hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<br>Sentiment: %{text}<extra></extra>'
            )
        )
        
        fig.update_layout(
            annotations=[
                dict(
                    x=0.5,
                    y=1.05,
                    xref="paper",
                    yref="paper",
                    text="Click on any point to see sentiment information",
                    showarrow=False,
                    font=dict(size=10, color="gray")
                )
            ]
        )
                
    if is_forecast:
        if 'forecast' in data.columns:
            historical = data[data['forecast'] == False]
            forecast = data[data['forecast'] == True]
            
            if not historical.empty and not forecast.empty:
                forecast_start_date = forecast['date'].min()
                forecast_start_str = forecast_start_date.strftime('%Y-%m-%d')
                
                fig.update_layout(
                    shapes=[
                        dict(
                            type="line",
                            xref="x",
                            yref="paper",
                            x0=forecast_start_str,
                            y0=0,
                            x1=forecast_start_str,
                            y1=1,
                            line=dict(
                                color="red",
                                width=2,
                                dash="dash",
                            )
                        )
                    ],
                    annotations=[
                        dict(
                            x=forecast_start_str,
                            y=1.0,
                            xref="x",
                            yref="paper",
                            text="Forecast Start",
                            showarrow=False,
                            xanchor="left",
                            font=dict(color="red")
                        )
                    ]
                )
    
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig
