Here’s your updated **Setup Instructions** with the note about changing the Vite port added at the end:

---

## Setup Instructions

Follow the steps below to customize the project for your own use:

1. **Update the Navbar**
   - Open `Navbar.jsx`
   - Replace **"My Project"** with your own project name.
   - Edit the `navItems` array to add, remove, or rename navigation links.

2. **Update the Footer**
   - Open `Footer.jsx`
   - Replace **"My Project"** with your own project name.

3. **Edit the HTML Entry File**
   - Open `index.html`
   - Update the project name in the `<title>` tag.

4. **Rename the Project**
   - Open `package.json` and `package-lock.json`
   - Replace `reduc-vite-auth-template` with your project name.

5. **Rename the App Folder**
   - Rename the `src/app-name` folder according to your project name.
   - This folder contains the project services.

6. **Change the Vite Port (Optional)**
   - Open `vite.config.js`
   - Add or modify the `server.port` property. From:

     ```js
     export default defineConfig({
       server: {
         port: 5178, // change to your preferred port
       },
       // other Vite config
     });
     ```
