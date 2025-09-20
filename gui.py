def plot_chart(self, data):

    for widget in self.chart_frame.winfo_children():
        widget.destroy()

    forecast = data.get("forecast")
    if not forecast:
        return

    import pandas as pd
    df = pd.DataFrame(forecast["list"])
    df["dt"] = pd.to_datetime(df["dt_txt"])
    df["date"] = df["dt"].dt.date
    df["temp_min"] = df["main"].apply(lambda x: x["temp_min"])
    df["temp_max"] = df["main"].apply(lambda x: x["temp_max"])
    grouped = df.groupby("date").agg({"temp_min": "min", "temp_max": "max"}).reset_index()


    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
    ax.plot(grouped["date"], grouped["temp_min"], marker="o", label="Min Temp (°C)", color="blue")
    ax.plot(grouped["date"], grouped["temp_max"], marker="o", label="Max Temp (°C)", color="red")
    ax.set_title(f"5-Day Forecast for {data.get('_display_name')}")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    fig.autofmt_xdate()


    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)