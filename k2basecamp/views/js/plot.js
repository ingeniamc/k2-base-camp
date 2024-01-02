const AXIS_MAXIMUM = 20;

/**
 * Initialize a chart with a spline series.
 * @param {ChartView} chart
 * @param {ValueAxis} xAxis
 * @param {ValueAxis} yAxis
 * @param {string} label
 */
function initSeries(chart, xAxis, yAxis, label) {
    const series = chart.createSeries(
        ChartView.SeriesTypeSpline,
        label,
        xAxis,
        yAxis
    );
    series.pointsVisible = true;
    series.color = "#80ff00";
}

/**
 * Reset the chart.
 * @param {ChartView} chart
 */
function resetPlot(chart) {
    const series = chart.series(0);
    const xAxis = chart.axisX(series);
    xAxis.min = 0;
    xAxis.max = AXIS_MAXIMUM;
    chart.removeAllSeries();
}

/**
 * Sets the y-axis display of the chart in a way that allows all values 
 * for a given velocity can comfortably be displayed.
 * @param {ChartView} chart
 * @param {float} velocity
 */
function setMaxVelocity(chart, velocity) {
    const series = chart.series(0);
    const yAxis = chart.axisY(series);
    yAxis.min = velocity * -1 - 2.5;
    yAxis.max = velocity + 2.5;
}

/**
 * Updates the chart as new values are coming in.
 * Moves the x-axis if the end of the current display has been reached.
 * @param {ChartView} chart 
 * @param {float} timestamp 
 * @param {float} velocity 
 */
function updatePlot(chart, timestamp, velocity) {
    const series = chart.series(0);
    const xAxis = chart.axisX(series);
    if (timestamp > AXIS_MAXIMUM) {
        xAxis.max = timestamp;
        xAxis.min = timestamp - AXIS_MAXIMUM;
    }
    series.append(timestamp, velocity);
}
