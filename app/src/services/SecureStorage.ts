import { Preferences } from '@capacitor/preferences';

export const SecureStorage = {
  setToken: async (token: string) => {
    await Preferences.set({
      key: 'jan_auth_token',
      value: token,
    });
  },
  getToken: async (): Promise<string | null> => {
    const { value } = await Preferences.get({ key: 'jan_auth_token' });
    return value;
  },
  removeToken: async () => {
    await Preferences.remove({ key: 'jan_auth_token' });
  },
  clearAll: async () => {
    await Preferences.clear();
  }
};
