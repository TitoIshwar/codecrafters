from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
from db import get_supabase
import os
from wordcloud import WordCloud # Corrected: Moved import to top

router = APIRouter()
supabase = get_supabase()

# Configure plot style
plt.style.use('seaborn-v0_8') # Updated style for newer matplotlib versions
sns.set_palette('husl')

# Directory for saving plots
CHARTS_DIR = 'static/charts'
os.makedirs(CHARTS_DIR, exist_ok=True)

@router.get('/analytics/task-completion')
async def task_completion_chart(user_id: str) -> FileResponse:
    """
    Generate task completion trend chart for the last 30 days.
    """
    try:
        # Fetch data for the last 30 days
        result = await supabase.table('daily_tasks') \
            .select('*') \
            .eq('user_id', user_id) \
            .gte('date', (datetime.now() - timedelta(days=30)).date().isoformat()) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail='No task data found for the last 30 days.')

        df = pd.DataFrame(result.data)
        df['date'] = pd.to_datetime(df['date'])

        # Ensure all dates in the range are present, fill missing with 0 completion
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
        daily_completion = df.groupby('date')['completed'].mean().reindex(date_range, fill_value=0)

        if daily_completion.empty:
            raise HTTPException(status_code=404, detail='No calculable completion data after processing.')

        plt.figure(figsize=(12, 6))
        daily_completion.plot(kind='line', marker='o')
        plt.title('Task Completion Trend (Last 30 Days)', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Average Completion Rate', fontsize=12)
        plt.ylim(-0.05, 1.05) # Ensure y-axis range for completion rate
        plt.grid(True)
        plt.tight_layout() # Adjust layout to prevent labels from overlapping

        filename = f'{CHARTS_DIR}/task_completion_{user_id}.png'
        plt.savefig(filename)
        plt.close() # Close the plot to free up memory
        return FileResponse(filename)
    except HTTPException as he:
        raise he # Re-raise HTTPException directly
    except Exception as e:
        print(f"Error in task_completion_chart: {e}") # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get('/analytics/mood-trend')
async def mood_trend_chart(user_id: str) -> FileResponse:
    """
    Generate mood trend chart based on reflections.
    Fetches all mood data for now, consider adding date range for large datasets.
    """
    try:
        # Fetch mood data. Consider adding a date filter for performance on large datasets:
        # .gte('timestamp', (datetime.now() - timedelta(days=90)).isoformat())
        result = await supabase.table('reflections') \
            .select('mood', 'timestamp') \
            .eq('user_id', user_id) \
            .order('timestamp') \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail='No mood data found for this user.')

        df = pd.DataFrame(result.data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Ensure there's data after converting to datetime (e.g., if parsing fails)
        if df['timestamp'].empty:
            raise HTTPException(status_code=404, detail='No valid timestamps found in mood data.')

        # Convert mood to numeric values
        mood_map = {
            "very sad": 1,
            "sad": 2,
            "neutral": 3,
            "happy": 4,
            "very happy": 5
        }
        df['mood_numeric'] = df['mood'].str.lower().map(mood_map)

        # Drop rows where mood could not be mapped
        df.dropna(subset=['mood_numeric'], inplace=True)

        if df['mood_numeric'].empty:
            raise HTTPException(status_code=404, detail='No valid mood values found after processing.')

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x='timestamp', y='mood_numeric', marker='o')
        plt.title('Mood Trend Over Time', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Mood Level', fontsize=12) # Changed label for clarity
        plt.yticks([1, 2, 3, 4, 5], ['Very Sad', 'Sad', 'Neutral', 'Happy', 'Very Happy'])
        plt.grid(True)
        plt.tight_layout()

        filename = f'{CHARTS_DIR}/mood_trend_{user_id}.png'
        plt.savefig(filename)
        plt.close()
        return FileResponse(filename)
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in mood_trend_chart: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.get('/analytics/feedback-wordcloud')
async def feedback_wordcloud(user_id: str) -> FileResponse:
    """
    Generate word cloud from user's feedback summaries.
    """
    try:
        result = await supabase.table('feedbacks') \
            .select('summary') \
            .eq('user_id', user_id) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail='No feedback data found for this user.')

        # Join all non-empty summaries into a single string
        text = ' '.join([f['summary'] for f in result.data if f and 'summary' in f and f['summary']])

        if not text:
            raise HTTPException(status_code=404, detail='No text content in feedback summaries to generate word cloud.')

        # You can add more customization to WordCloud here (e.g., stopwords, max_words)
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            collocations=False, # Often better for general text to avoid 'word word' pairs
            min_font_size=10
        ).generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off') # Hide axes
        plt.title('Common Words in Feedback', fontsize=16) # Add a title
        plt.tight_layout()

        filename = f'{CHARTS_DIR}/feedback_wordcloud_{user_id}.png'
        plt.savefig(filename)
        plt.close()
        return FileResponse(filename)
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in feedback_wordcloud: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")