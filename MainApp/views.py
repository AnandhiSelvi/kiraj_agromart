import csv
import io
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.core.files.storage import FileSystemStorage
from .models import Candle

class UploadCSVView(View):
    def get(self, request):
        return render(request, 'upload_csv.html')

    def post(self, request):
            print("hellooo")
        # try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)

            candles = self.process_uploaded_file(uploaded_file)

            timeframe = int(request.POST.get('timeframe', 1))
            converted_candles = self.convert_to_timeframe(candles, timeframe)

            # Generate the text file with processed data
            file_path = self.generate_text_file(converted_candles)
            print(file_path)

            # Return the file path for download
            return JsonResponse({'file_path': file_path})

        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=400)

    def process_uploaded_file(self, uploaded_file):
        text_data = uploaded_file.read().decode('utf-8')
        csv_data = io.StringIO(text_data)
        reader = csv.reader(csv_data)
        next(reader)  # Skip header row if exists

        candles = []
        for row in reader:
            try:
                candle = self.create_candle_from_row(row)
                candles.append(candle)
            except (ValueError, IndexError) as e:
                raise ValueError(f"Error processing row {row}: {e}")
        return candles

    def create_candle_from_row(self, row):
        date_str, time_str = row[1], row[2]
        date_time = datetime.strptime(date_str + ' ' + time_str, '%Y%m%d %H:%M')
        date_time = timezone.make_aware(date_time, timezone.get_default_timezone())

        open_price = float(row[3])
        high_price = float(row[4])
        low_price = float(row[5])
        close_price = float(row[6])
        try:
            volume = int(float(row[7]))
        except:
            volume=0
        return Candle(
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
            date=date_time
        )

    def convert_to_timeframe(self, candles, timeframe_minutes):
        timeframe_candles = []
        i = 0
        while i < len(candles):
            chunk = candles[i:i + timeframe_minutes]
            timeframe_candle = self.create_timeframe_candle(chunk)
            timeframe_candles.append(timeframe_candle)
            i += timeframe_minutes
        return timeframe_candles

    def create_timeframe_candle(self, candles_chunk):
        date = candles_chunk[0].date
        open_price = candles_chunk[0].open
        high_price = max(c.high for c in candles_chunk)
        low_price = min(c.low for c in candles_chunk)
        close_price = candles_chunk[-1].close
        volume = sum(c.volume for c in candles_chunk)

        return Candle(
            date=date,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        )

    def generate_text_file(self, candles):
        file_content = ""
        for candle in candles:
            file_content += f"{candle.date}, {candle.open}, {candle.high}, {candle.low}, {candle.close}, {candle.volume}\n"

        file_name = "processed_data.txt"
        fs = FileSystemStorage()
        file_path = fs.save(file_name, io.BytesIO(file_content.encode('utf-8')))
        print("hellothere")
        return fs.url(file_path)
