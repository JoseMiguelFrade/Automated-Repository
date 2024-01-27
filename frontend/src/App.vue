<template>
  <v-app>
    <navbar></navbar>
    <v-main> <!-- This will ensure content is below the navbar -->
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/NavBar.vue';

export default {
  name: 'App',
  components: {
    Navbar
  }
}
</script>