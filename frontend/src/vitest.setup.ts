import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
import fetch, { Request, Response, Headers } from 'node-fetch';
// Override JSDOM fetch with node-fetch or native fetch
if (!globalThis.fetch) {
  // globalThis.fetch = fetch as any;
}
