<template>
  <v-container>
    <!-- URL Input with Integrated File Upload -->
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="pa-4" outlined elevation="2">
          <v-row>
            <v-col cols="12">
              <v-text-field
                label="Enter URL or Upload a List"
                v-model="inputUrl"
                @input="clearFileSelection"
                outlined
                :append-inner-icon="'mdi-upload'"
                @click:append-inner="openFileUpload"
              ></v-text-field>
              <input
                type="file"
                ref="fileInput"
                style="display: none"
                @change="handleFileUpload"
                accept=".txt"
              />
              <v-label v-if="selectedFileName">List Selected: {{ selectedFileName }}</v-label>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-radio-group v-model="crawlMode" row>
                <v-radio label="Crawl in Depth" value="depth"></v-radio>
                <v-radio label="Crawl in All Directions" value="all"></v-radio>
              </v-radio-group>
            </v-col>
          </v-row>
          <v-row v-if="crawlMode === 'depth'">
            <v-col cols="12">
              <v-select
                label="Select Depth"
                :items="[1, 2, 3, 4, 5, 6, 7]"
                v-model="depth"
                outlined
              ></v-select>
            </v-col>
          </v-row>
          <v-row v-else>
            <v-col cols="12">
              <v-select
                label="Select Depth"
                :items="[1, 2, 3, 4]"
                v-model="depth"
                outlined
              ></v-select>
            </v-col>
          </v-row>
          <v-row justify="center" class="mt-3">
            <v-btn color="primary" @click="launchCrawler" class="mx-2">
              <v-icon left>mdi-play</v-icon>
              Launch
            </v-btn>
            <v-btn color="red" @click="stopCrawler" class="mx-2">
              <v-icon left>mdi-stop</v-icon>
              Stop
            </v-btn>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!-- Enhanced List for Displaying Crawled URLs -->
    <v-row justify="center" v-if="isCrawlerStarted">
      <v-col cols="12" sm="8" md="6">
        <v-card class="mt-5" outlined elevation="2">
          <v-card-title class="blue darken-1 white--text">Crawled URLs</v-card-title>
          <v-list>
            <v-list-item v-for="(url, index) in urls" :key="index">
              <v-list-item-content>
                <v-list-item-title>{{ url }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';
import io from 'socket.io-client';

const apiUrl = import.meta.env.VITE_API_URL;

export default {
  data() {
    return {
      urls: [],
      depth: 1,
      socket: null,
      inputUrl: '',
      uploadedUrls: [],
      isCrawlerStarted: false,
      selectedFileName: '',
      crawlMode: 'depth', // Default mode
    };
  },
  methods: {
    openFileUpload() {
      this.inputUrl = ''; // Clear text input
      this.$refs.fileInput.click();
    },
    clearFileSelection() {
      this.$refs.fileInput.value = ''; // Clear file input
      this.uploadedUrls = [];
      this.selectedFileName = '';
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file && file.type === 'text/plain') {
        this.selectedFileName = file.name; // Set selected file name
        const reader = new FileReader();
        reader.onload = (e) => {
          this.uploadedUrls = e.target.result.split(/\r?\n/).filter((url) => url.trim() !== '');
        };
        reader.readAsText(file);
      } else {
        console.log('Please select a .txt file');
      }
    },
    launchCrawler() {
      let urlsToCrawl = this.inputUrl ? [this.inputUrl.trim()] : [];
      if (this.uploadedUrls.length) {
        urlsToCrawl = urlsToCrawl.concat(this.uploadedUrls);
      }
      if (urlsToCrawl.length) {
        axios.post(`${apiUrl}/start-crawler`, {
          urls: urlsToCrawl,
          depth: this.depth,
          crawl_in_depth: this.crawlMode === 'depth', // Pass the crawl mode as a boolean
        })
          .then(response => console.log('Crawler launched successfully:', response.data))
          .catch(error => console.error('Error launching crawler:', error));
        this.isCrawlerStarted = true;
      } else {
        console.log('Please enter a URL or upload a list of URLs');
      }
    },
    stopCrawler() {
      axios.post(`${apiUrl}/stop-crawler`)
        .then(response => {
          console.log('Crawler stopped successfully:', response.data);
        })
        .catch(error => {
          console.error('Error stopping crawler:', error);
        });
    },
  },
  mounted() {
    this.socket = io(`${apiUrl}`);

    this.socket.on('connect', () => {
      console.log('Socket.IO connected');
    });

    this.socket.on('new_url', (data) => {
      console.log('Received URL:', data.url);
      this.urls.push(data.url);

      // Keep only the latest 20 links
      if (this.urls.length > 20) {
        this.urls.shift(); // Remove the oldest link
      }
    });

    this.socket.on('disconnect', () => {
      console.log('Socket.IO disconnected');
    });
  },
};
</script>

<style scoped>
/* Additional styles can be applied here if necessary */
</style>
