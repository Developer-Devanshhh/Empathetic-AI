import { pipeline } from '@xenova/transformers';

/**
 * Singleton class to manage the embedding model.
 * Using a singleton pattern ensures we only load the model once.
 */
class EmbeddingPipeline {
  static task = 'feature-extraction';
  static model = 'Xenova/all-MiniLM-L6-v2';
  static instance = null;

  static async getInstance(progress_callback = null) {
    if (this.instance === null) {
      this.instance = pipeline(this.task, this.model, { progress_callback });
    }
    return this.instance;
  }
}

/**
 * Generates an embedding for the given text.
 * @param {string} text 
 * @returns {Promise<number[]>} The 384-dimensional vector as an array.
 */
export async function generateEmbedding(text) {
  const extractor = await EmbeddingPipeline.getInstance();
  const output = await extractor(text, { pooling: 'mean', normalize: true });
  return Array.from(output.data);
}
