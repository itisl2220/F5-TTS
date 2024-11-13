<!-- omit in toc -->
# Shared Model Cards

<!-- omit in toc -->
### **Prerequisites of using**
- This document is serving as a quick lookup table for the community training/finetuning result, with various language support.
- The models in this repository are open source and are based on voluntary contributions from contributors.
- The use of models must be conditioned on respect for the respective creators. The convenience brought comes from their efforts.

<!-- omit in toc -->
### **Welcome to share here**
- Have a pretrained/finetuned result: model checkpoint (pruned best to facilitate inference, i.e. leave only `ema_model_state_dict`) and corresponding vocab file (for tokenization).
- Host a public [huggingface model repository](https://huggingface.co/new) and upload the model related files.
- Make a pull request adding a model card to the current page, i.e. `src\f5_tts\infer\SHARED.md`.

<!-- omit in toc -->
### Supported Languages
- [Multilingual](#multilingual)
    - [F5-TTS Base @ pretrain @ zh \& en](#f5-tts-base--pretrain--zh--en)
- [Mandarin](#mandarin)
- [English](#english)
- [French](#french)


## Multilingual

#### F5-TTS Base @ pretrain @ zh & en
|Model|🤗Hugging Face|Data (Hours)|Model License|
|:---:|:------------:|:-----------:|:-------------:|
|F5-TTS Base|[ckpt & vocab](https://huggingface.co/SWivid/F5-TTS/tree/main/F5TTS_Base)|[Emilia 95K zh&en](https://huggingface.co/datasets/amphion/Emilia-Dataset/tree/fc71e07)|cc-by-nc-4.0|

```bash
MODEL_CKPT: hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors
VOCAB_FILE: hf://SWivid/F5-TTS/F5TTS_Base/vocab.txt
```
*Other infos, e.g. Author info, Github repo, Link to some sampled results, Usage instruction, Tutorial (Blog, Video, etc.) ...*

## Mandarin


## English

## French
|Model|🤗Hugging Face|Data (Hours)|Model License|
|:---:|:------------:|:-----------:|:-------------:|
|F5-TTS French|[ckpt & vocab](https://huggingface.co/RASPIAUDIO/F5-French-MixedSpeakers-reduced)|[LibriVox](https://librivox.org/)|cc-by-nc-4.0|

```bash
MODEL_CKPT: hf://RASPIAUDIO/F5-French-MixedSpeakers-reduced/model_last_reduced.pt
VOCAB_FILE: hf://RASPIAUDIO/F5-French-MixedSpeakers-reduced/vocab.txt
```
### Online Inference
You can test the model online using our [Hugging Face Space](https://huggingface.co/spaces/RASPIAUDIO/f5-tts_french).

### Resources
- [Tutorial video to train a new language model](https://www.youtube.com/watch?v=UO4usaOojys)
- [Discussion about this training can be found here](https://github.com/SWivid/F5-TTS/issues/434)

