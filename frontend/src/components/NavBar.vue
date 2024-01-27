<template>
    <v-app-bar app>
        <v-toolbar-title>CiberLaw</v-toolbar-title>
        <v-spacer></v-spacer>

        <!-- Home Button -->
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn color="primary" v-bind="props" to="/">Home</v-btn>
            </template>
        </v-menu>

        <!-- Keywords Menu -->
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn color="primary" v-bind="props" @click="openFileUpload">
                    Keywords
                </v-btn>
            </template>
        </v-menu>
        <!-- Invisible File Input -->
        <input type="file" ref="fileInput" @change="handleFileUpload" accept=".txt" style="display: none;" />

        <!-- Crawler Menu -->
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn color="primary" v-bind="props" to="/crawler">Crawler</v-btn>
            </template>
        </v-menu>

                <!-- Repository Menu -->
                <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn color="primary" v-bind="props">Repository</v-btn>
            </template>
            <v-list>
                <v-list-item :to="{ name: 'Repository' }">
                    <v-list-item-title>Open</v-list-item-title>
                </v-list-item>
                <v-list-item @click="UpdateRepo">
                    <v-list-item-title>Update</v-list-item-title>
                </v-list-item>
                <v-list-item :to="{ name: 'NetworkGraph' }">
                    <v-list-item-title>Graph</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>


    </v-app-bar>
</template>

  
<script>
import axios from 'axios';
export default {
    name: 'Navbar',
    methods: {
        stopCrawler() {
            // Replace with your API URL
            const apiUrl = import.meta.env.VITE_API_URL;

            axios.post(`${apiUrl}/stop-crawler`)
                .then(response => {
                    console.log('Crawler stopped successfully:', response.data);
                    // Handle successful response
                })
                .catch(error => {
                    console.error('Error stopping crawler:', error);
                    // Handle error response
                });
        },
        openFileUpload() {
            this.$refs.fileInput.click(); // Trigger file input click event
        },
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file && file.type === 'text/plain') {
                this.uploadKeywords(file);
            } else {
                console.log('Please select a .txt file containing keywords');
            }
        },
        uploadKeywords(file) {
            // Replace with your API URL and endpoint for file upload
            const apiUrl = import.meta.env.VITE_API_URL;
            const formData = new FormData();
            formData.append('file', file);

            axios.post(`${apiUrl}/upload-keywords`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
                .then(response => {
                    console.log('Keywords uploaded successfully:', response.data);
                    // Handle successful response
                })
                .catch(error => {
                    console.error('Error uploading keywords:', error);
                    // Handle error response
                });
        },
        UpdateRepo() {
           
            const apiUrl = import.meta.env.VITE_API_URL;

            axios.post(`${apiUrl}/update-repo`)
                .then(response => {
                    console.log('Repository updated successfully:', response.data);
                    // Handle successful response
                })
                .catch(error => {
                    console.error('Error updating repository:', error);
                    // Handle error response
                });
        }
    }
};
</script>;
  