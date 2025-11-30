import '@testing-library/jest-dom';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({}),
    text: async () => '',
  });
});

afterEach(() => {
  jest.clearAllMocks();
});
