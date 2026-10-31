import http from 'k6/http';
import { check, sleep } from 'k6';

const baseURL = (__ENV.K6_BASE_URL || '').replace(/\/$/, '');
const allow = __ENV.ALLOW_LOAD_TEST === 'YES';
const parsed = baseURL.match(/^http:\/\/(localhost|127(?:\.\d{1,3}){3}|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?::\d+)?$/);

if (!allow) {
  throw new Error('Refusing to run: set ALLOW_LOAD_TEST=YES after confirming authorization.');
}
if (!parsed) {
  throw new Error('Refusing to run: K6_BASE_URL must be http://localhost, loopback, or RFC1918 IPv4.');
}

export const options = {
  scenarios: {
    capacity: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '30s', target: 250 },
        { duration: '45s', target: 1000 },
        { duration: '60s', target: 2500 },
        { duration: '60s', target: 5000 },
        { duration: '60s', target: 10000 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<1500', 'p(99)<4000'],
    checks: ['rate>0.98'],
  },
  discardResponseBodies: true,
};

export default function () {
  const health = http.get(`${baseURL}/health`, { tags: { endpoint: 'health' }, timeout: '10s' });
  check(health, {
    'health responds 200': (r) => r.status === 200,
  });

  // No credentials and no state-changing request: this should be denied.
  const protectedRead = http.get(`${baseURL}/billing/fee-types`, {
    tags: { endpoint: 'protected_read_unauthenticated' },
    timeout: '10s',
  });
  check(protectedRead, {
    'protected finance route rejects anonymous request': (r) => r.status === 401 || r.status === 403,
  });
  sleep(0.1);
}
