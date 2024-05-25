import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/components/Home.vue'; // Assuming you have a Home.vue
import CrawlerMenu from '@/components/CrawlerMenu.vue';
import Repository from '@/components/Repository.vue';
import Details from '@/components/Details.vue';
import EditDocument from '@/components/EditDocument.vue';
import Regenerate from '@/components/Regenerate.vue';
import NetworkGraph from '@/components/NetworkGraph.vue';
import Statistics from '@/components/Statistics.vue';
import Update from '@/components/Update.vue';
import NewDocuments from '@/components/NewDocuments.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/crawler:filename?',
    name: 'Crawler',
    component: CrawlerMenu,
    props: route => ({ urls: route.query.urls }),
  },
  {
    path: '/repository',
    name: 'Repository',
    component: Repository
  },
  {
    path: '/details/:id',
    name: 'Details',
    component: Details
  },
  {
    path: '/edit-document/:id',
    name: 'EditDocument',
    component: EditDocument
  },
  {
    path: '/regenerate/:id',
    name: 'Regenerate',
    component: Regenerate
  },
  {
    path: '/network-graph',
    name: 'NetworkGraph',
    component: NetworkGraph
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  },
  {
    path: '/update',
    name: 'Update',
    component: Update
  },
  {
    path: '/new-documents',
    name: 'NewDocuments',
    component: NewDocuments
  }


];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;