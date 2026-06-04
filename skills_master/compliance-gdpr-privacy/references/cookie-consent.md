# Cookie Consent Implementation

## React Consent Banner Component

```tsx
'use client';

import { useState, useEffect, useCallback } from 'react';

type CookieCategory = 'necessary' | 'functional' | 'analytics' | 'marketing';

interface ConsentState {
  necessary: true;
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
  timestamp: number;
  version: string;
}

const CONSENT_KEY = 'cookie-consent';
const CONSENT_VERSION = '1.0';

function getStoredConsent(): ConsentState | null {
  if (typeof window === 'undefined') return null;
  try {
    const stored = localStorage.getItem(CONSENT_KEY);
    if (!stored) return null;
    const parsed = JSON.parse(stored);
    // Re-consent if version changed
    if (parsed.version !== CONSENT_VERSION) return null;
    return parsed;
  } catch {
    return null;
  }
}

function storeConsent(consent: ConsentState): void {
  localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
}

export function CookieConsentBanner() {
  const [consent, setConsent] = useState<ConsentState | null>(null);
  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    const stored = getStoredConsent();
    if (stored) {
      setConsent(stored);
      applyConsent(stored);
    } else {
      setShowBanner(true);
      // Set default denied state for Google Consent Mode
      setDefaultConsent();
    }
  }, []);

  const handleAcceptAll = useCallback(() => {
    const newConsent: ConsentState = {
      necessary: true, functional: true, analytics: true, marketing: true,
      timestamp: Date.now(), version: CONSENT_VERSION,
    };
    setConsent(newConsent);
    storeConsent(newConsent);
    applyConsent(newConsent);
    setShowBanner(false);
  }, []);

  const handleRejectAll = useCallback(() => {
    const newConsent: ConsentState = {
      necessary: true, functional: false, analytics: false, marketing: false,
      timestamp: Date.now(), version: CONSENT_VERSION,
    };
    setConsent(newConsent);
    storeConsent(newConsent);
    applyConsent(newConsent);
    setShowBanner(false);
  }, []);

  const handleSavePreferences = useCallback((prefs: Partial<ConsentState>) => {
    const newConsent: ConsentState = {
      necessary: true,
      functional: prefs.functional ?? false,
      analytics: prefs.analytics ?? false,
      marketing: prefs.marketing ?? false,
      timestamp: Date.now(),
      version: CONSENT_VERSION,
    };
    setConsent(newConsent);
    storeConsent(newConsent);
    applyConsent(newConsent);
    setShowBanner(false);
  }, []);

  if (!showBanner) return null;

  return (
    <div
      role="dialog"
      aria-label="Cookie consent"
      className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t shadow-lg p-6"
    >
      {!showDetails ? (
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-sm text-gray-600">
              We use cookies to enhance your experience. By continuing to visit this site you agree
              to our use of necessary cookies.{' '}
              <button onClick={() => setShowDetails(true)} className="text-blue-600 underline">
                Manage preferences
              </button>
            </p>
          </div>
          <div className="flex gap-3">
            <button onClick={handleRejectAll}
              className="px-4 py-2 text-sm border rounded-lg hover:bg-gray-50">
              Reject All
            </button>
            <button onClick={handleAcceptAll}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Accept All
            </button>
          </div>
        </div>
      ) : (
        <CookiePreferences
          onSave={handleSavePreferences}
          onClose={() => setShowDetails(false)}
        />
      )}
    </div>
  );
}
```

## Cookie Category Details Panel

```tsx
interface CategoryInfo {
  key: CookieCategory;
  title: string;
  description: string;
  required: boolean;
  cookies: Array<{ name: string; purpose: string; duration: string }>;
}

const categories: CategoryInfo[] = [
  {
    key: 'necessary',
    title: 'Strictly Necessary',
    description: 'Essential for the website to function. Cannot be disabled.',
    required: true,
    cookies: [
      { name: 'session_id', purpose: 'User session management', duration: 'Session' },
      { name: 'csrf_token', purpose: 'CSRF protection', duration: 'Session' },
      { name: 'cookie-consent', purpose: 'Stores your consent preferences', duration: '1 year' },
    ],
  },
  {
    key: 'functional',
    title: 'Functional',
    description: 'Enable personalized features like language and region.',
    required: false,
    cookies: [
      { name: 'locale', purpose: 'Language preference', duration: '1 year' },
      { name: 'theme', purpose: 'UI theme preference', duration: '1 year' },
    ],
  },
  {
    key: 'analytics',
    title: 'Analytics',
    description: 'Help us understand how visitors interact with our website.',
    required: false,
    cookies: [
      { name: '_ga', purpose: 'Google Analytics visitor ID', duration: '2 years' },
      { name: '_ga_*', purpose: 'Google Analytics session', duration: '2 years' },
    ],
  },
  {
    key: 'marketing',
    title: 'Marketing',
    description: 'Used to deliver relevant advertisements and track campaigns.',
    required: false,
    cookies: [
      { name: '_fbp', purpose: 'Facebook Pixel tracking', duration: '3 months' },
      { name: '_gcl_au', purpose: 'Google Ads conversion tracking', duration: '3 months' },
    ],
  },
];

function CookiePreferences({
  onSave,
  onClose,
}: {
  onSave: (prefs: Partial<ConsentState>) => void;
  onClose: () => void;
}) {
  const [prefs, setPrefs] = useState({
    functional: false,
    analytics: false,
    marketing: false,
  });

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-lg font-semibold mb-4">Cookie Preferences</h2>
      <div className="space-y-4 mb-6">
        {categories.map((cat) => (
          <div key={cat.key} className="border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">{cat.title}</h3>
                <p className="text-sm text-gray-500">{cat.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={cat.required || prefs[cat.key as keyof typeof prefs] || false}
                  disabled={cat.required}
                  onChange={(e) => setPrefs({ ...prefs, [cat.key]: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-blue-600
                  peer-disabled:bg-green-500 peer-disabled:cursor-not-allowed
                  after:content-[''] after:absolute after:top-0.5 after:left-[2px]
                  after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all
                  peer-checked:after:translate-x-full" />
              </label>
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="px-4 py-2 text-sm border rounded-lg">Back</button>
        <button onClick={() => onSave(prefs)}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
          Save Preferences
        </button>
      </div>
    </div>
  );
}
```

## Third-Party Script Blocking

```typescript
// Block scripts until consent is given
function loadScript(src: string, id?: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (id && document.getElementById(id)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    if (id) script.id = id;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });
}

function removeScript(id: string): void {
  const script = document.getElementById(id);
  if (script) script.remove();
}

function applyConsent(consent: ConsentState): void {
  // Analytics
  if (consent.analytics) {
    loadScript(`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`, 'ga-script');
  } else {
    removeScript('ga-script');
    // Clear analytics cookies
    deleteCookie('_ga');
    deleteCookie('_ga_' + GA_ID.replace('G-', ''));
  }

  // Marketing
  if (consent.marketing) {
    loadScript('https://connect.facebook.net/en_US/fbevents.js', 'fb-pixel');
  } else {
    removeScript('fb-pixel');
    deleteCookie('_fbp');
  }

  // Update Google Consent Mode v2
  updateGoogleConsent(consent);
}

function deleteCookie(name: string): void {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.${window.location.hostname}`;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}
```

## Google Consent Mode v2

```html
<!-- Must be the FIRST script in <head> -->
<script>
  // Set default consent state BEFORE loading GTM
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}

  gtag('consent', 'default', {
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': 'denied',
    'functionality_storage': 'denied',
    'personalization_storage': 'denied',
    'security_storage': 'granted',
    'wait_for_update': 500,  // Wait 500ms for consent banner
  });
</script>

<!-- Then load GTM -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
```

```typescript
function setDefaultConsent(): void {
  window.gtag?.('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'denied',
    personalization_storage: 'denied',
    security_storage: 'granted',
    wait_for_update: 500,
  });
}

function updateGoogleConsent(consent: ConsentState): void {
  window.gtag?.('consent', 'update', {
    analytics_storage: consent.analytics ? 'granted' : 'denied',
    ad_storage: consent.marketing ? 'granted' : 'denied',
    ad_user_data: consent.marketing ? 'granted' : 'denied',
    ad_personalization: consent.marketing ? 'granted' : 'denied',
    functionality_storage: consent.functional ? 'granted' : 'denied',
    personalization_storage: consent.functional ? 'granted' : 'denied',
  });
}

// Type declaration
declare global {
  interface Window {
    dataLayer: any[];
    gtag: (...args: any[]) => void;
  }
}
```

## Server-Side Consent Logging

```typescript
// API route: POST /api/consent
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();

  const consentRecord = {
    userId: body.userId || null,
    sessionId: request.cookies.get('session_id')?.value,
    consent: {
      necessary: true,
      functional: body.functional ?? false,
      analytics: body.analytics ?? false,
      marketing: body.marketing ?? false,
    },
    timestamp: new Date().toISOString(),
    policyVersion: body.version,
    ipAddress: request.headers.get('x-forwarded-for') || request.ip,
    userAgent: request.headers.get('user-agent'),
    source: body.source || 'banner', // 'banner' | 'settings' | 'api'
  };

  // Store in append-only audit table
  await db.consentAuditLog.insert(consentRecord);

  return NextResponse.json({ success: true });
}
```
