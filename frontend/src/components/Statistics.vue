<template>
    <v-container>
        <v-row>
            <v-col cols="12" md="12">
                <canvas id="areaChart"></canvas>
                <!-- Centered Radio Buttons for Issuer -->
                <v-row justify="center">
                    <v-col cols="auto">
                        <v-radio-group v-model="selectedIssuer" @change="fetchAreaData" row>
                            <v-radio label="All" value="all"></v-radio>
                            <v-radio label="ENISA" value="enisa"></v-radio>
                            <v-radio label="CNCS" value="cncs"></v-radio>
                            <v-radio label="Assembleia da República" value="assembleia"></v-radio>
                            <v-radio label="EU" value="eu"></v-radio>
                        </v-radio-group>
                    </v-col>
                </v-row>
            </v-col>
            <v-col cols="12" md="12">
                <canvas id="documentCountChart"></canvas>
                <!-- Centered Radio Buttons -->
                <v-row justify="center">
                    <v-col cols="auto">
                        <v-radio-group v-model="selectedOrigin" @change="fetchDocumentCountsByYear" row>
                            <v-radio label="All" value="all"></v-radio>
                            <v-radio label="Portugal" value="Portugal"></v-radio>
                            <v-radio label="EU" value="EU"></v-radio>
                        </v-radio-group>
                    </v-col>
                </v-row>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12" md="12">
                <canvas id="monthlyDocumentCountChart"></canvas>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12" md="12">
                <canvas id="documentTypeChart"></canvas>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12" md="6">
                <canvas id="radarChart1"></canvas>
            </v-col>
            <v-col cols="12" md="6">
                <canvas id="radarChart2"></canvas>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12" md="6">
                <canvas id="radarChart3"></canvas>
            </v-col>
            <v-col cols="12" md="6">
                <canvas id="radarChart4"></canvas>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);
const apiUrl = import.meta.env.VITE_API_URL;

export default {
    name: 'Statistics',
    data() {
        return {
            selectedOrigin: 'all',
            selectedIssuer: 'all',  // default selected issuer
            charts: {},
            chartInstances: [null, null, null, null],
        };
    },
    mounted() {
        this.fetchAreaData();
        this.fetchDocumentCountsByYear();
        this.fetchAreaDataByYear();
        this.fetchDocumentCountsByMonth();
        this.fetchDocumentCountsByType();  // Fetch document counts by type
    },
    methods: {
        fetchAreaData() {
            axios.get(`${apiUrl}/areas`, { params: { issuer: this.selectedIssuer } })
                .then(response => {
                    console.log(response.data);
                    const areaData = response.data;
                    const sortedAreaData = Object.entries(areaData)
                        .sort((a, b) => b[1] - a[1]); // Sort by count descending
                    const labels = sortedAreaData.map(item => item[0]);
                    const counts = sortedAreaData.map(item => item[1]);
                    this.createChart(labels, counts, 'areaChart', 'Number of Documents by Area');
                })
                .catch(error => {
                    console.error("Error fetching area data:", error);
                });
        },
        fetchDocumentCountsByYear() {
            axios.get(`${apiUrl}/document_counts_by_year`, { params: { origin: this.selectedOrigin } })
                .then(response => {
                    const yearData = response.data;
                    const years = yearData.map(item => item.year);
                    const counts = yearData.map(item => item.count);
                    this.createChart(years, counts, 'documentCountChart', 'Document Count Over Time', 'line');
                })
                .catch(error => {
                    console.error("Error fetching document counts by year:", error);
                });
        },
        fetchDocumentCountsByMonth() {
            axios.get(`${apiUrl}/document_counts_by_month`)
                .then(response => {
                    const monthData = response.data;
                    const months = monthData.map(item => item.yearMonth);
                    const counts = monthData.map(item => item.count);
                    this.createChart(months, counts, 'monthlyDocumentCountChart', 'Cumulative Document Count Over Time', 'line');
                })
                .catch(error => {
                    console.error("Error fetching document counts by month:", error);
                });
        },
        fetchDocumentCountsByType() {
            axios.get(`${apiUrl}/document_counts_by_type`)
                .then(response => {
                    const typeData = response.data;
                    const types = typeData.map(item => item.type);
                    const counts = typeData.map(item => item.count);
                    this.createChart(types, counts, 'documentTypeChart', 'Document Count by Type');
                })
                .catch(error => {
                    console.error("Error fetching document counts by type:", error);
                });
        },
        createChart(labels, data, canvasId, chartLabel, type = 'bar') {
            if (this.charts[canvasId]) {
                this.charts[canvasId].destroy();
            }
            const ctx = document.getElementById(canvasId).getContext('2d');
            const myChart = new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: chartLabel,
                        data: data,
                        backgroundColor: type === 'line' ? 'rgba(54, 162, 235, 0.5)' : 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        fill: type === 'line' ? false : true
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            this.charts[canvasId] = myChart;
        },
        fetchAreaDataByYear() {
            axios.get(`${apiUrl}/area_counts_by_year`)
                .then(response => {
                    const data = response.data;
                    this.createRadarCharts(data);
                })
                .catch(error => {
                    console.error("Error fetching area counts by year:", error);
                });
        },
        createRadarCharts(data) {
            const allAreas = Array.from(new Set(data.flatMap(year => year.areas.map(area => area.area))));
            const groupSize = Math.ceil(allAreas.length / 4);
            const areaGroups = [];
    
            for (let i = 0; i < 4; i++) {
                areaGroups[i] = allAreas.slice(i * groupSize, (i + 1) * groupSize);
            }

            areaGroups.forEach((group, index) => {
                const chartId = `radarChart${index + 1}`;
                const datasets = group.map((area, areaIndex) => {
                    const areaData = data.map(year => {
                        const areaEntry = year.areas.find(a => a.area === area);
                        return areaEntry ? areaEntry.count : 0;
                    });
                    return {
                        label: area,
                        data: areaData,
                        fill: false,
                        borderColor: this.getRandomColor(areaIndex),
                        pointBackgroundColor: this.getRandomColor(areaIndex),
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: this.getRandomColor(areaIndex, 0.8),
                        borderWidth: 2
                    };
                });

                const ctx = document.getElementById(chartId).getContext('2d');
                if (this.chartInstances[index]) {
                    this.chartInstances[index].destroy();
                }
                this.chartInstances[index] = new Chart(ctx, {
                    type: 'radar',
                    data: {
                        labels: data.map(item => item.year),
                        datasets: datasets
                    },
                    options: {
                        elements: {
                            line: {
                                borderWidth: 3
                            }
                        },
                        scale: {
                            angleLines: {
                                display: true
                            },
                            ticks: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top'
                            }
                        }
                    }
                });
            });
        },
        getRandomColor(index, opacity = 1) {
            const colors = [
                'rgba(255, 99, 132,',
                'rgba(54, 162, 235,',
                'rgba(255, 206, 86,',
                'rgba(75, 192, 192,',
                'rgba(153, 102, 255,'
            ];
            return colors[index % colors.length] + opacity + ')';
        }
    }
}
</script>

<style scoped></style>
