# Visual Direction Plan

Create `visual-plan.json` before generating assets. It is specific to the current brand and topic, never a fixed visual template.

```json
{
  "brand": {"name": "", "handle": ""},
  "direction": {
    "mood": "editorial, warm, and practical",
    "palette": ["#19212B", "#536B78", "#F7F3EA", "#E26D3D"]
  },
  "slides": [
    {
      "carousel": 1,
      "slide": 1,
      "role": "cover",
      "image": "carousel-01-slide-01.png",
      "image_prompt": "A single subject that expresses the cover idea"
    }
  ]
}
```

Choose the direction from the topic, audience, tone, and supplied brand materials. Vary each slide's visual subject while keeping the palette and editorial character coherent.

For generated imagery, ask for an image without text, logo, watermark, frame, or interface. The compositor adds the exact slide text afterwards.
