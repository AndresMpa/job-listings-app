import { readFileSync } from 'fs';
import { resolve } from 'path';

export default defineEventHandler(() => {
  const filePath = resolve('data.json');
  const data = JSON.parse(readFileSync(filePath, 'utf-8'));
  return data;
});