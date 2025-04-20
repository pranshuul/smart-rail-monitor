async function fetchData() {
  const resp = await fetch('/data');
  return resp.json();
}
async function fetchAccuracy() {
  const resp = await fetch('/accuracy');
  return resp.json();
}
function createChart(ctx, label, data, borderColor, yMin = 0, yMax = 8) {
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(r => new Date(r.created_at)),
      datasets: [{
        label,
        data: data.map(r => r[label]),
        tension: 0.4,
        borderColor
      }]
    },
    options: {
      scales: {
        x: {
          type: 'time',
          time: {
            tooltipFormat: 'MMM d, h:mm a'
          },
          min: new Date('2025-04-16T00:00:00'),
          // max: new Date('2025-04-20T23:59:59'),
          title: {
            display: true,
            text: 'Timestamp'
          }
        },
        y: {
          min: yMin,
          max: yMax,
          title: {
            display: true,
            text: 'Value'
          }
        }
      }
    }
  });
}

(async ()=>{
  const data = await fetchData();
createChart(document.getElementById('chart1'), 'field1', data, 'var(--teal)');              // y: 0–8
createChart(document.getElementById('chart2'), 'field2', data, 'var(--teal)');              // y: 0–8
createChart(document.getElementById('chart3'), 'field3', data, 'var(--orange)', 0, 1);      // y: 0–1
createChart(document.getElementById('chart4'), 'field4', data, 'var(--orange)', 0, 1);      // y: 0–1
createChart(document.getElementById('alertSensor'), 'field5', data, '#dc3545', 0, 1);       // y: 0–1
createChart(document.getElementById('alertML'), 'field6', data, '#ffc107', 0, 1);           // y: 0–1

  const acc = await fetchAccuracy();
  document.getElementById('accuracyMeter').innerText = acc.accuracy + '%';

  document.getElementById('triggerSensor').onclick = ()=>fetch('/trigger', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'sensor'})});
  document.getElementById('triggerML').onclick     = ()=>fetch('/trigger', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'ml'})});
})();
