import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.janai.app',
  appName: 'jan-ai',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    cleartext: true,
  }
};

export default config;
