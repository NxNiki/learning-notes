Run the following command to start docker image:

```
docker run --gpus all --ipc=host --net=host \
    -v /home/ec2-user/SageMaker/Xin:/workspace \
    --ulimit memlock=-1 --ulimit stack=67108864 \
    -it --rm nvcr.io/nvidia/pytorch:25.02-py3 bash
```

To avoiding having to start container from scrach every time:

```
docker run --gpus all --ipc=host --net=host \
    -v /home/ec2-user/SageMaker/Xin:/workspace \
    --ulimit memlock=-1 --ulimit stack=67108864 \
    -it --name higgs_container nvcr.io/nvidia/pytorch:25.02-py3 bash
```

restart the container:

```
docker start -ai higgs_container
```


Clone repo and install dependencies in a virtual environment:
```
git clone https://github.com/boson-ai/higgs-audio.git
cd higgs-audio

python3 -m venv higgs_audio_env
source higgs_audio_env/bin/activate
pip install -r requirements.txt
pip install -e .
```

Add fork repo:

```
git remote add fork https://github.com/Nyarlth/higgs-audio_quantized.git
git fetch fork
git checkout -b fork-branch fork/main
```


redirect huggingface cache to avoid out of space error:
```
export HF_HOME=/workspace/huggingface_cache
export TRANSFORMERS_CACHE=/workspace/huggingface_cache
mkdir -p /workspace/huggingface_cache
```

Run the following example:
```
python3 examples/generation.py \
--transcript "The sun rises in the east and sets in the west. This simple fact has been observed by humans for thousands of years." \
--ref_audio belinda \
--temperature 0.3 \
--out_path generation.wav
```

out of memory trouble shoot:

https://github.com/boson-ai/higgs-audio/issues/48
