# Music Analysis Platform - Frontend

Next.js frontend for the Music Analysis Platform with TypeScript, React Query, and Tailwind CSS.

## Features

- 🎵 **Music Library**: Browse and manage songs
- 📥 **YouTube Import**: Import songs from YouTube with real-time progress
- ✏️ **Arrangement Editor**: Edit sections, chords, and arrangement details
- 📋 **Setlist Manager**: Create and manage worship setlists
- 🎤 **Live Mode**: Stage presentation with large typography
- 🔐 **Authentication**: JWT-based auth with role-based access control
- 🎨 **Modern UI**: Tailwind CSS with dark theme

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **State Management**: Zustand
- **Data Fetching**: React Query + Axios
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form + Zod
- **UI Components**: Custom + Lucide icons

## Setup

### Prerequisites

- Node.js 18+
- npm or pnpm

### Installation

```bash
cd apps/web
npm install
# or
pnpm install
```

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Development

```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm run start
```

### Testing

```bash
npm run test
npm run test:watch
npm run test:coverage
```

## Project Structure

```
src/
├── components/        # Reusable components
│   └── Layout.tsx    # Main layout wrapper
├── pages/            # Next.js pages
│   ├── _app.tsx      # App initialization
│   ├── login.tsx     # Login page
│   ├── library.tsx   # Music library
│   ├── import.tsx    # YouTube import
│   ├── arrangements/ # Arrangement editor
│   ├── setlists/     # Setlist manager
│   └── live/         # Live mode
├── services/         # API client
│   └── api.ts       # Centralized API
├── store/           # Zustand stores
│   └── auth.ts      # Auth state
├── styles/          # Global styles
│   └── globals.css
└── types/           # TypeScript types
```

## API Integration

The frontend communicates with the FastAPI backend via the `apiClient` service:

```typescript
import { apiClient } from '@/services/api';

// Import song
const result = await apiClient.importYoutube('https://youtube.com/...');

// Get analysis status
const status = await apiClient.getAnalysisStatus(analysisId);

// Create arrangement
const arrangement = await apiClient.createArrangement(songId, {
  name: 'My Arrangement',
  key: 'G major',
});
```

## Authentication

The app uses JWT tokens stored in Zustand:

```typescript
import { useAuthStore } from '@/store/auth';

const { user, login, logout } = useAuthStore();

// Login
await login(email, password, organizationId);

// Logout
await logout();
```

## Pages

### Library (`/library`)
Browse all songs in the organization library with pagination.

### Import (`/import`)
Import songs from YouTube with real-time progress tracking through all analysis phases.

### Arrangement Editor (`/arrangements/[id]`)
Edit sections, chords, and arrangement details. Publish when ready.

### Setlist Manager (`/setlists`)
Create and manage worship setlists. Add published arrangements.

### Live Mode (`/live/[id]`)
Stage presentation mode with large typography, navigation, and upcoming songs preview.

## Styling

The app uses Tailwind CSS with a dark theme:

- **Primary**: Blue (`#3b82f6`)
- **Background**: Slate 900 (`#0f172a`)
- **Surface**: Slate 700 (`#334155`)
- **Text**: Slate 50 (`#f8fafc`)

Customize in `tailwind.config.js`.

## Performance

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Built-in Next.js Image component
- **Caching**: React Query with configurable stale time
- **Lazy Loading**: Dynamic imports for heavy components

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
docker build -t music-analysis-web .
docker run -p 3000:3000 music-analysis-web
```

### Environment Variables for Production

```env
NEXT_PUBLIC_API_URL=https://api.example.com
```

## Troubleshooting

### API Connection Issues

- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running on the correct port
- Check CORS headers in backend

### Authentication Issues

- Clear browser cookies and localStorage
- Check JWT token expiration
- Verify organization ID is correct

### Build Issues

```bash
# Clear cache
rm -rf .next
npm run build
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `npm run test`
4. Submit a pull request

## License

MIT
