# JAN AI - Play Store Release Process

The JAN AI application is fully configured as a Capacitor Mobile Application wrapper around the React Vite SPA. Here are the exact instructions to build the final production payload required by the Google Play Console for distribution.

## Prerequisites
1. Ensure you have Android Studio installed.
2. The `janai.keystore` file has been generated inside `app/android/app/`.

## Step 1: Build the Web Artifacts
The React application must be packaged before Native sync.
```bash
cd app
npm run build
npx cap sync android
```

## Step 2: Configure the Release Key
Update the `app/android/app/build.gradle` file to reference the generated keystore so the binaries are cryptographically signed.

```gradle
android {
    ...
    signingConfigs {
        release {
            storeFile file("janai.keystore")
            storePassword "janpass123"
            keyAlias "janai"
            keyPassword "janpass123"
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

## Step 3: Generate the Android App Bundle (.aab)
Google Play requires the modern `.aab` format instead of legacy `.apk`s to optimize downloads for end users.

1. Open Android Studio inside the `app/android` directory.
2. Allow Gradle to finish its initial sync.
3. In the top menu, go to **Build > Generate Signed Bundle / APK...**
4. Select **Android App Bundle** and click Next.
5. Select the `janai.keystore` generated in this folder. Enter `janpass123` for both passwords.
6. Select the **release** build variant and click Finish.

The signed `.aab` will be exported to `app/android/app/release/app-release.aab`.

## Step 4: Play Store Upload
1. Log into the Google Play Console.
2. Create a new App named **JAN AI: Marketing OS**.
3. Navigate to **Store presence > Main store listing** and populate the Data from the `playstore/` directory.
   - Upload the custom App Icon (1024x1024) and Feature Graphic inside `playstore/assets/`.
   - Copy the short/full descriptions from `app_description.txt`.
4. Register the privacy policy URL.
5. Create a Production track release and upload the `app-release.aab`.
6. Submit for review!
