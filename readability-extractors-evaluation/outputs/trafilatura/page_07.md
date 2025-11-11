# Transformer (deep learning)

[Transformer (deep learning architecture)](/w/index.php?title=Transformer_(deep_learning_architecture)&redirect=no))

| Part of a series on |
and
|
|---|

![](//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/250px-Transformer%2C_full_architecture.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/250px-Transformer%2C_full_architecture.png)

In [deep learning](/wiki/Deep_learning), the **transformer** is a neural network architecture based on the multi-head [attention](/wiki/Attention_(machine_learning)) mechanism, in which text is converted to numerical representations called [tokens](/wiki/Large_language_model#Tokenization), and each token is converted into a vector via lookup from a [word embedding](/wiki/Word_embedding) table. [1] At each layer, each

[token](/wiki/Tokenization_(lexical_analysis))is then

[contextualized](/wiki/Contextualization_(computer_science))within the scope of the

[context window](/wiki/Context_window)with other (unmasked) tokens via a parallel multi-head attention mechanism, allowing the signal for key tokens to be amplified and less important tokens to be diminished.

Transformers have the advantage of having no recurrent units, therefore requiring less training time than earlier [recurrent neural architectures](/wiki/Recurrent_neural_network) (RNNs) such as [long short-term memory](/wiki/Long_short-term_memory) (LSTM). [2] Later variations have been widely adopted for training

[large language models](/wiki/Large_language_model)(LLMs) on large (language)

[datasets](/wiki/Training,_validation,_and_test_data_sets).


[[3]](#cite_note-:7-3)
The modern version of the transformer was proposed in the 2017 paper "[Attention Is All You Need](/wiki/Attention_Is_All_You_Need)" by researchers at [Google](/wiki/Google). [1] The predecessors of transformers were developed as an improvement over previous architectures for

[machine translation](/wiki/Machine_translation),


[[4]](#cite_note-inventors-4)but have found many applications since. They are used in large-scale

[[5]](#cite_note-inventconfirm-5)[natural language processing](/wiki/Natural_language_processing),

[computer vision](/wiki/Computer_vision)(

[vision transformers](/wiki/Vision_transformer)),

[reinforcement learning](/wiki/Reinforcement_learning),


[[6]](#cite_note-:10-6)

[[7]](#cite_note-7)[audio](/wiki/Audio_signal_processing),


[[8]](#cite_note-Robust_Speech_Recognition_via_Large-Scale_Weak_Supervision-8)[multimodal learning](/wiki/Multimodal_learning),

[robotics](/wiki/Robotics),

and even playing

[[9]](#cite_note-9)[chess](/wiki/Computer_chess).

It has also led to the development of

[[10]](#cite_note-grandmaster-10)[pre-trained systems](/wiki/Transfer_learning), such as

[generative pre-trained transformers](/wiki/Generative_pre-trained_transformer)(GPTs)

and

[[11]](#cite_note-wolf2020-11)[BERT](/wiki/BERT_(language_model))

(bidirectional encoder representations from transformers).

[[12]](#cite_note-:6-12)## History

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=1)]

### Predecessors

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=2)]

For many years, sequence modelling and generation was done by using plain [recurrent neural networks](/wiki/Recurrent_neural_network) (RNNs). A well-cited early example was the [Elman network](/wiki/Elman_network) (1990). In theory, the information from one token can propagate arbitrarily far down the sequence, but in practice the [vanishing-gradient problem](/wiki/Vanishing-gradient_problem) leaves the model's state at the end of a long sentence without precise, extractable information about preceding tokens.

A key breakthrough was [LSTM](/wiki/Long_short-term_memory) (1995), [note 1] an RNN which used various innovations to overcome the vanishing gradient problem, allowing efficient learning of long-sequence modelling. One key innovation was the use of an

[attention mechanism](/wiki/Attention_(machine_learning))which used neurons that multiply the outputs of other neurons, so-called

*multiplicative units*.

Neural networks using multiplicative units were later called

[[13]](#cite_note-14)*sigma-pi networks*

or

[[14]](#cite_note-PDP-15)*.*

[higher-order networks](/w/index.php?title=Higher-order_neural_network&action=edit&redlink=1)LSTM became the standard architecture for long sequence modelling until the 2017 publication of transformers. However, LSTM still used sequential processing, like most other RNNs.

[[15]](#cite_note-16)Specifically, RNNs operate one token at a time from first to last; they cannot operate in parallel over all tokens in a sequence.

[[note 2]](#cite_note-17)Modern transformers overcome this problem, but unlike RNNs, they require computation time that is [quadratic](/wiki/Quadratic_function) in the size of the context window. The linearly scaling [fast weight](/w/index.php?title=Fast_weight&action=edit&redlink=1) controller (1992) learns to compute a weight matrix for further processing depending on the input. [16] One of its two networks has "fast weights" or "dynamic links" (1981).


[[17]](#cite_note-malsburg1981-19)

[[18]](#cite_note-feldman1982-20)A slow neural network learns by gradient descent to generate keys and values for computing the weight changes of the fast neural network which computes answers to queries.

[[19]](#cite_note-21)This was later shown to be equivalent to the unnormalized linear transformer.

[[16]](#cite_note-transform19922-18)

[[20]](#cite_note-fastlinear20202-22)

[[21]](#cite_note-schlag20212-23)### Attention with seq2seq

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=3)]

The idea of encoder–decoder sequence transduction had been developed in the early 2010s; commonly cited as the originators that produced seq2seq are two concurrently published papers from 2014.[[22]](#cite_note-:22-24)[[23]](#cite_note-sequence-25)

A 380M-parameter model for machine translation uses two [long short-term memories](/wiki/Long_short-term_memory) (LSTM). [23] Its architecture consists of two parts. The

*encoder*is an LSTM that takes in a sequence of tokens and turns it into a vector. The

*decoder*is another LSTM that converts the vector into a sequence of tokens. Similarly, another 130M-parameter model used

[gated recurrent units](/wiki/Gated_recurrent_unit)(GRU) instead of LSTM.

Later research showed that GRUs are neither better nor worse than LSTMs for seq2seq.

[[22]](#cite_note-:22-24)

[[24]](#cite_note-MyUser_Arxiv.org_May_18_2016c-26)

[[25]](#cite_note-gruber_jockisch-27)These early seq2seq models had no attention mechanism, and the state vector is accessible only after the *last* word of the source text was processed. Although in theory such a vector retains the information about the whole original sentence, in practice the information is poorly preserved. This is because the input is processed sequentially by one recurrent network into a *fixed*-size output vector, which is then processed by another recurrent network into an output. If the input is long, then the output vector would not be able to contain all relevant information, degrading the output. As evidence, reversing the input sentence improved seq2seq translation.[[26]](#cite_note-28)

The *RNN search* model introduced an attention mechanism to seq2seq for machine translation to solve the bottleneck problem (of the *fixed-size* output vector), allowing the model to process long-distance dependencies more easily. The name is because it "emulates searching through a source sentence during decoding a translation".[[4]](#cite_note-inventors-4)

The relative performances were compared between global (that of *RNN search*) and local (sliding window) attention model architectures for machine translation, finding that mixed attention had higher quality than global attention, while local attention reduced translation time.[[27]](#cite_note-29)

In 2016, [Google Translate](/wiki/Google_Translate) was revamped to [Google Neural Machine Translation](/wiki/Google_Neural_Machine_Translation), which replaced the previous model based on [statistical machine translation](/wiki/Statistical_machine_translation). The new model was a seq2seq model where the encoder and the decoder were both 8 layers of bidirectional LSTM. [28] It took nine months to develop, and it outperformed the statistical approach, which took ten years to develop.


[[29]](#cite_note-UJDu8-31)### Parallelizing attention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=4)]

Seq2seq models with attention (including self-attention) still suffered from the same issue with recurrent networks, which is that they are hard to [parallelize](/wiki/Parallel_computing), which prevented them from being accelerated on GPUs. In 2016, *decomposable attention* applied a self-attention mechanism to [feedforward networks](/wiki/Feedforward_neural_network), which are easy to parallelize, and achieved [SOTA](/wiki/State_of_the_art) result in [textual entailment](/wiki/Textual_entailment) with an order of magnitude fewer parameters than LSTMs. [30] One of its authors, Jakob Uszkoreit, suspected that attention

*without*recurrence would be sufficient for language translation, thus the title "attention is

*all*you need".

That hypothesis was against conventional wisdom at the time, and even his father

[[31]](#cite_note-:11-33)[Hans Uszkoreit](/wiki/Hans_Uszkoreit), a well-known computational linguist, was skeptical.

In the same year, self-attention (called

[[31]](#cite_note-:11-33)*intra-attention or*

*intra-sentence attention*) was proposed for LSTMs.


[[32]](#cite_note-34)In 2017, the original (100M-sized) encoder–decoder transformer model was proposed in the "[Attention is all you need](/wiki/Attention_is_all_you_need)" paper. At the time, the focus of the research was on improving [seq2seq](/wiki/Seq2seq) for [machine translation](/wiki/Machine_translation), by removing its recurrence to process all tokens in parallel, but preserving its dot-product attention mechanism to keep its text processing performance. [1] This led to the introduction of a multi-head attention model that was easier to parallelize due to the use of independent heads and the lack of recurrence. Its parallelizability was an important factor to its widespread use in large neural networks.


[[33]](#cite_note-35)### AI boom era

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=5)]

Already in spring 2017, even before the "Attention is all you need" preprint was published, one of the co-authors applied the "decoder-only" variation of the architecture to generate fictitious Wikipedia articles. [34] Transformer architecture is now used alongside many

[generative models](/wiki/Generative_artificial_intelligence)that contribute to the ongoing

[AI boom](/wiki/AI_boom).

In language modelling, [ELMo](/wiki/ELMo) (2018) was a bi-directional LSTM that produces contextualized [word embeddings](/wiki/Word_embedding), improving upon the line of research from [bag of words](/wiki/Bag-of-words_model) and [word2vec](/wiki/Word2vec). It was followed by [BERT](/wiki/BERT_(language_model)) (2018), an encoder-only transformer model. [35] In 2019 October, Google started using BERT to process search queries.

In 2020, Google Translate replaced the previous RNN-encoder–RNN-decoder model by a transformer-encoder–RNN-decoder model.

[[36]](#cite_note-38)

[[37]](#cite_note-gtrans-39)Starting in 2018, the OpenAI [GPT series](/wiki/Generative_pre-trained_transformer) of decoder-only transformers became state of the art in [natural language generation](/wiki/Natural_language_generation). In 2022, a chatbot based on GPT-3, [ChatGPT](/wiki/ChatGPT), became unexpectedly [38] popular, triggering a boom around

[large language models](/wiki/Large_language_model).


[[39]](#cite_note-gpt12-41)

[[40]](#cite_note-ngEG3-42)Since 2020, transformers have been applied in modalities beyond text, including the [vision transformer](/wiki/Vision_transformer), [41] speech recognition,

robotics,

[[42]](#cite_note-Gulati2020-44)and

[[6]](#cite_note-:10-6)[multimodal](/wiki/Multimodal_learning).

The vision transformer, in turn, stimulated new developments in

[[43]](#cite_note-choromanski2020-45)[convolutional neural networks](/wiki/Convolutional_neural_network).

Image and video generators like

[[44]](#cite_note-46)[DALL-E](/wiki/DALL-E)(2021),

[Stable Diffusion 3](/wiki/Stable_Diffusion)(2024),

and

[[45]](#cite_note-:62-47)[Sora](/wiki/Sora_(text-to-video_model))(2024), use transformers to analyse input data (like text prompts) by breaking it down into "tokens" and then calculating the relevance between each token using self-attention, which helps the model understand the context and relationships within the data.

## Training

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=6)]

### Methods for stabilizing training

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=7)]

The plain transformer architecture had difficulty in converging. In the original paper, [1] the authors recommended using

[learning rate](/wiki/Learning_rate)warmup. That is, the learning rate should linearly scale up from 0 to maximal value for the first part of the training (usually recommended to be 2% of the total number of training steps), before decaying again.

A 2020 paper found that using [layer normalization](/wiki/Layer_normalization) *before* (instead of after) multihead attention and feedforward layers stabilizes training, not requiring learning rate warmup.[[46]](#cite_note-auto1-48)

### Pretrain-finetune

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=8)]

Transformers typically are first pretrained by [self-supervised learning](/wiki/Self-supervised_learning) on a large generic dataset, followed by [supervised](/wiki/Supervised_learning) [fine-tuning](/wiki/Fine-tuning_(deep_learning)) on a small task-specific dataset. The pretrain dataset is typically an unlabeled large corpus, such as [The Pile](/wiki/The_Pile_(dataset)). Tasks for pretraining and fine-tuning commonly include:

[language modeling](/wiki/Language_modeling)[[12]](#cite_note-:6-12)- next-sentence prediction
[[12]](#cite_note-:6-12) [question answering](/wiki/Question_answering)[[3]](#cite_note-:7-3)[reading comprehension](/wiki/Natural-language_understanding)[sentiment analysis](/wiki/Sentiment_analysis)[[1]](#cite_note-2017_Attention_Is_All_You_Need-1)[paraphrasing](/wiki/Text_Summaries)[[1]](#cite_note-2017_Attention_Is_All_You_Need-1)

The [T5 transformer](/wiki/T5_(language_model)) report [47] documents a large number of

[natural language](/wiki/Natural_language)pretraining tasks. Some examples are:

- restoring or repairing incomplete or corrupted text. For example, the input,
*"Thank you ~~ me to your party ~~ week",*might generate the output,*"Thank you***for inviting**me to your party**last**week". - translation between natural languages (
[machine translation](/wiki/Machine_translation)) - judging the pragmatic acceptability of natural language. For example, the following sentence might be judged "not acceptable",
because even though it is syntactically well-formed, it is improbable in ordinary human usage:[[48]](#cite_note-50)*The course is jumping well.*

Note that while each of these tasks is trivial or obvious for human native speakers of the language (or languages), they have typically proved challenging for previous generations of machine learning architecture.

### Tasks

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=9)]

In general, there are 3 classes of language modelling tasks: "masked", [49] "autoregressive",

and "prefixLM".

[[50]](#cite_note-:8-52)These classes are independent of a specific modeling architecture such as transformer, but they are often discussed in the context of transformer.

[[51]](#cite_note-:4-53)In a masked task, [49] one or more of the tokens is masked out, and the model would produce a probability distribution predicting what the masked-out tokens are based on the context. The

[loss function](/wiki/Loss_function)for the task is typically sum of

[log-perplexities](/wiki/Perplexity)for the masked-out tokens: and the model is trained to minimize this loss function. The

[BERT series of models](/wiki/BERT_(language_model))are trained for masked token prediction and another task.

In an autoregressive task, [50] the entire sequence is masked at first, and the model produces a probability distribution for the first token. Then the first token is revealed and the model predicts the second token, and so on. The loss function for the task is still typically the same. The

[GPT series of models](/wiki/Generative_pre-trained_transformer)are trained by autoregressive tasks.

In a prefixLM task, [51] the sequence is divided into two parts. The first part is presented as context, and the model predicts the first token of the second part. Then that would be revealed, and the model predicts the second token, and so on. The loss function for the task is still typically the same. The

[T5 series of models](/wiki/T5_(language_model))are trained by prefixLM tasks.

Note that "masked" as in "masked language modelling" is not "masked" as in "[masked attention](#Masked_attention)", and "prefixLM" as in
"prefix language modeling" is not "prefixLM" as in " [prefix language model](#prefixLM)".

## Architecture

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=10)]

All transformers have the same primary components:

- Tokenizers, which convert text into tokens.
- Embedding layer, which converts tokens and positions of the tokens into vector representations.
- Transformer layers, which carry out repeated transformations on the vector representations, extracting more and more linguistic information. These consist of alternating attention and feedforward layers. There are two major types of transformer layers: encoder layers and decoder layers, with further variants.
- Un-embedding layer, which converts the final vector representations back to a probability distribution over the tokens.

The following description follows exactly the transformer as described in the original paper. There are variants, described in the [following section](#Subsequent_work).

By convention, we write all vectors as row vectors. For example, pushing a vector through a linear layer means multiplying it by a weight matrix on the right, as .

### Tokenization

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=11)]

As the transformer architecture natively consists of operations over numbers (matrix multiplications, dot products, activation functions) rather than over text, there must first be a mapping from any input text to some numerical representation. This happens in three steps.

First, the input text is treated by a *preprocessor*, which performs both textual transformations and splits the text into coarse-grained segments called *pretokens*. The latter is referred to as *pretokenization*. Second, each pretoken is segmented further into *tokens* by a *tokenizer* that expects to only see pretokens output by its preprocessor. Each token it produces is a string of one or more characters belonging to a finite set of strings called the *vocabulary* . Third, because the vocabulary is finite and known beforehand, each token can be assigned an integer identifier, and this mapping is applied to the sequence of tokens to represent any input text as a numerical sequence. Since this mapping is bijective, the output side can produce a sequence of integer identifiers which can then be turned back into tokens. After undoing some of the preprocessing, the result is again legible text.

Training a tokenizer (sometimes referred to as *vocabularization*) means finding a suitable vocabulary , but also learning how to use it, since any given string of length has hypothetical segmentations, some of which containing segments that are not in the vocabulary. The most important hyperparameter during vocabularization is the *vocabulary size* : when it is small, the learned vocabulary generally consists of characters and smaller strings, and words will be segmented into many tokens. At larger sizes, it becomes affordable to dedicate tokens to full words, although depending on the preprocessor and tokenizer, it is not necessarily the case that large vocabularies will always use the largest token(s) available to segment a word.

Because tokens are not always full words, they may also be referred to as *subwords* and tokenization algorithms may be referred to as *subword tokenizers*. This is also to differentiate these systems from [traditional terminology](/wiki/Lexical_analysis) used in older information retrieval and natural language processing systems, where "tokenization" was used to denote what is today called "pretokenization" (very crudely: splitting into words). In tokenizers that produce tokens that are *not* part of the vocabulary, a special token that does belong to the vocabulary is used as a generic stand-in, written as "[UNK]" for "unknown". In principle, any string could be hidden by such an [UNK]. Indeed, in information retrieval, pretokenizers were themselves used as tokenizers (and also called "tokenizers") with a word-level vocabulary that contained an [UNK].

Commonly used subword tokenization algorithms are [byte pair encoding](/wiki/Byte_pair_encoding) (BPE) and the unigram language model (ULM), which each include a vocabularization algorithm and a dedicated segmentation algorithm. There also exist several segmentation algorithms that require no learning and can be applied given a vocabulary (produced by BPE or ULM, for example), like greedily recognising tokens in a pretoken by moving through it left-to-right. Well-known software implementations of subword tokenizers are [Hugging Face](/wiki/Hugging_Face)'s `tokenizers`

Python package implemented in Rust, and the `sentencepiece`

Python package implemented in C++. The latter package is named as such because one of its configuration options allows disabling the built-in pretokenizer, hence effectively making entire sentences a pretoken and thus having the tokenizer see entire sentences, rather than individual words.

### Embedding

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=12)]

Each integer token identifier is converted into an embedding vector via a [lookup table](/wiki/Lookup_table). Equivalently stated, it multiplies a [one-hot](/wiki/One-hot) representation of the token identifier by an embedding matrix . For example, if the input token's identifier is , then the one-hot representation is , and its embedding vector isThe token embedding vectors are added to their respective positional encoding vectors (see below), producing the sequence of input vectors.

The dimension of an embedding vector is called *hidden size* or *embedding size* and written as . [35] This size is written as in the original transformer paper.


[[1]](#cite_note-2017_Attention_Is_All_You_Need-1)### Un-embedding

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=13)]

An un-embedding layer is almost the reverse of an embedding layer. Whereas an embedding layer converts a token identifier into a vector, an un-embedding layer converts a vector into a probability distribution over tokens.

The un-embedding layer is a linear-[softmax](/wiki/Softmax_function) layer:The matrix has shape . Some architectures use the transpose of the embedding matrix as the un-embedding matrix in order to avoid needing double the amount of embedding-related parameters and to avoid divergence during training. This practice is called *weight tying*.[[52]](#cite_note-54)

### Positional encoding

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=14)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/0/02/Positional_encoding.png/250px-Positional_encoding.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Positional_encoding.png/250px-Positional_encoding.png)

[sinusoidal](/wiki/Sine_wave)positional encoding with parameters

A positional encoding is a fixed-size vector representation of the relative positions of tokens within a sequence: it provides the transformer model with information about *where* the words are in the input sequence. This induces a [bias](/wiki/Inductive_bias) towards the order of the input sequence, so that, for example, the input sequence "[man bites dog](/wiki/Man_bites_dog)" is processed differently from "dog bites man".

The positional encoding is defined as a function of type , where is a positive even [integer](/wiki/Integer). The full positional encoding defined in the original paper [1] is:where .

Here, is a free parameter that should be significantly larger than the biggest that would be input into the positional encoding function. The original paper uses .

The function is in a simpler form when written as a complex function of type where .

The main reason for using this positional encoding function is that using it, shifts are linear transformations:where is the distance one wishes to shift. This allows the transformer to take any encoded position, and find the encoding of the position n-steps-ahead or n-steps-behind, by a matrix multiplication.

By taking a linear sum, any convolution can also be implemented as linear transformations:for any constants . This allows the transformer to take any encoded position and find a linear sum of the encoded locations of its neighbors. This sum of encoded positions, when fed into the attention mechanism, would create attention weights on its neighbors, much like what happens in a [convolutional neural network](/wiki/Convolutional_neural_network) [language model](/wiki/Language_model). In the author's words, "we hypothesized it would allow the model to easily learn to attend by relative position."

In typical implementations, all operations are done over the real numbers, not the complex numbers, but since [complex multiplication can be implemented as real 2-by-2 matrix multiplication](/wiki/Complex_number#Matrix_representation_of_complex_numbers), this is a mere notational difference.

### Encoder–decoder (overview)

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=15)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/5/53/Transformer%2C_one_encoder-decoder_block.png/250px-Transformer%2C_one_encoder-decoder_block.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Transformer%2C_one_encoder-decoder_block.png/250px-Transformer%2C_one_encoder-decoder_block.png)

![](//upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Transformer%2C_stacked_layers_and_sublayers.png/250px-Transformer%2C_stacked_layers_and_sublayers.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Transformer%2C_stacked_layers_and_sublayers.png/250px-Transformer%2C_stacked_layers_and_sublayers.png)

Like earlier [seq2seq](/wiki/Seq2seq) models, the original transformer model used an **encoder–decoder** architecture. The encoder consists of encoding layers that process all the input tokens together one layer after another, while the decoder consists of decoding layers that iteratively process the encoder's output and the decoder's output tokens so far.

The purpose of each encoder layer is to create contextualized representations of the tokens, where each representation corresponds to a token that "mixes" information from other input tokens via self-attention mechanism. Each decoder layer contains two attention sublayers: (1) cross-attention for incorporating the output of encoder (contextualized input token representations), and (2) self-attention for "mixing" information among the input tokens to the decoder (i.e. the tokens generated so far during inference time).[[53]](#cite_note-55)[[54]](#cite_note-:1-56)

Both the encoder and decoder layers have a [feed-forward neural network](/wiki/Feedforward_neural_network) for additional processing of their outputs and contain residual connections and layer normalization steps. [54] These feed-forward layers contain most of the parameters in a transformer model.

### Feedforward network

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=16)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/5/59/Transformer_architecture_-_FFN_module.png/250px-Transformer_architecture_-_FFN_module.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Transformer_architecture_-_FFN_module.png/250px-Transformer_architecture_-_FFN_module.png)

The feedforward network (FFN) modules in a transformer are 2-layered [multilayer perceptrons](/wiki/Feedforward_neural_network):where and are weight matrices and and are bias vectors, and is its activation function. The original transformer used [ReLU](/wiki/Rectifier_(neural_networks)) activation.

The number of neurons in the middle layer is called *intermediate size* (GPT),[[55]](#cite_note-57)*filter size* (BERT), [35] or

*feedforward size*(BERT).

It is typically larger than the embedding size. For example, in both GPT-2 series and BERT series, the intermediate size of a model is 4 times its embedding size: .

[[35]](#cite_note-:03-37)### Scaled dot-product attention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=17)]

#### Attention head

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=18)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Transformer%2C_attention_block_diagram.png/250px-Transformer%2C_attention_block_diagram.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Transformer%2C_attention_block_diagram.png/250px-Transformer%2C_attention_block_diagram.png)

![](//upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Transformer_architecture_-_Attention_Head_module.png/250px-Transformer_architecture_-_Attention_Head_module.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Transformer_architecture_-_Attention_Head_module.png/250px-Transformer_architecture_-_Attention_Head_module.png)

The attention mechanism used in the transformer architecture are scaled [dot-product](/wiki/Dot_product) [attention](/wiki/Attention_(machine_learning)) units. For each unit, the transformer model learns three weight matrices: the query weights , the key weights , and the value weights .

The module takes three sequences, a query sequence, a key sequence, and a value sequence. The query sequence is a sequence of length , and each entry is a vector of dimension . Similarly for the key and value sequences.

For each vector in the query sequence, it is multiplied by a matrix to produce a query vector . The matrix of all query vectors is the query matrix:Similarly, we construct the key matrix and the value matrix .

It is usually the case that all are square matrices, meaning , etc.

Attention weights are calculated using the query and key vectors: the attention weight from token to token is the [dot product](/wiki/Dot_product) between and . The attention weights are divided by the square root of the dimension of the key vectors, , which stabilizes gradients during training, and passed through a [softmax](/wiki/Softmax_function) which normalizes the weights. The fact that and are different matrices allows attention to be non-symmetric: if token attends to token (i.e. is large), this does not necessarily mean that token will attend to token (i.e. could be small). The output of the attention unit for token is the weighted sum of the value vectors of all tokens, weighted by , the attention from token to each token.

The attention calculation for all tokens can be expressed as one large matrix calculation using the [softmax function](/wiki/Softmax_function), which is useful for training due to computational matrix operation optimizations that quickly compute matrix operations. The matrices , and are defined as the matrices where the th rows are vectors , , and respectively. Then we can represent the attention as

where the softmax is applied over each of the rows of the matrix.

The number of dimensions in a query vector is *query size* and similarly for the *key size* and *value size* . The output dimension of an attention head is its *head dimension* . The attention mechanism requires the following three equalities to hold:but is otherwise unconstrained.

If the attention head is used in a self-attention fashion, then . If the attention head is used in a cross-attention fashion, then usually . It is theoretically possible for all three to be different, but that is rarely the case in practice.

#### Multihead attention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=19)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Multiheaded_attention%2C_block_diagram.png/250px-Multiheaded_attention%2C_block_diagram.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Multiheaded_attention%2C_block_diagram.png/250px-Multiheaded_attention%2C_block_diagram.png)

![](//upload.wikimedia.org/wikipedia/commons/thumb/1/15/Transformer_architecture_-_Multiheaded_Attention_module.png/250px-Transformer_architecture_-_Multiheaded_Attention_module.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Transformer_architecture_-_Multiheaded_Attention_module.png/250px-Transformer_architecture_-_Multiheaded_Attention_module.png)

One set of matrices is called an *attention head*, and each layer in a transformer model has multiple attention heads. While each attention head attends to the tokens that are relevant to each token, multiple attention heads allow the model to do this for different definitions of "relevance". Specifically, the query and key projection matrices, and , which are involved in the attention score computation, defines the "relevance". Meanwhile, the value [projection matrix](/wiki/Projection_matrix) , in combination with the part of the output projection matrix , determines how the attended tokens influence what information is passed to subsequent layers and ultimately the output logits. In addition, the scope of attention, or the range of token relationships captured by each attention head, can expand as tokens pass through successive layers. This allows the model to capture more complex and long-range dependencies in deeper layers. Many transformer attention heads encode relevance relations that are meaningful to humans. For example, some attention heads can attend mostly to the next word, while others mainly attend from verbs to their direct objects. [56] The computations for each attention head can be performed in

[parallel](/wiki/Parallel_computing), which allows for fast processing. The outputs for the attention layer are concatenated to pass into the

[feedforward neural network](/wiki/Feedforward_neural_network)layers.

Concretely, let the multiple attention heads be indexed by , then we have where the matrix is the concatenation of word embeddings, and the matrices are "projection matrices" owned by individual attention head , and is a final projection matrix owned by the whole multihead attention head.

It is theoretically possible for each attention head to have a different head dimension , but that is rarely the case in practice.

As an example, in the smallest GPT-2 model, there are only self-attention mechanisms. It has the following dimensions:Since , its output projection matrix is a square matrix.

#### Masked attention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=20)]

The transformer architecture is constructed to calculate output tokens iteratively. Assuming refers to the calculation of the first output token , for step , the output token shall remain constant. This ensures properties of the model similar to [autoregressive models](/wiki/Autoregressive_models). [1] Therefore, at every time step , the calculation for all outputs should not have access to tokens at position for (as it naturally is the case for time step , when tokens are not yet calculated). This behavior may be accomplished before the softmax stage by adding a mask matrix that is at entries where the attention link must be cut, and at other places: The following matrix is commonly used in decoder self-attention modules, called "causal masking":

In words, it means that each token can pay attention to itself, and every token before it, but not any after it. A non-masked attention module can be thought of as a masked attention module where the mask has all entries zero. As an example of an uncommon use of mask matrix, the [XLNet](/wiki/XLNet) considers all masks of the form , where is a random [permutation matrix](/wiki/Permutation_matrix).[[57]](#cite_note-59)

### Encoder

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=21)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Transformer%2C_one_encoder_block.png/250px-Transformer%2C_one_encoder_block.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Transformer%2C_one_encoder_block.png/250px-Transformer%2C_one_encoder_block.png)

An encoder consists of an embedding layer, followed by multiple encoder layers.

Each encoder layer consists of two major components: a self-attention mechanism and a feed-forward layer. It takes an input as a sequence of input vectors, applies the self-attention mechanism, to produce an intermediate sequence of vectors, then applies the feed-forward layer for each vector individually. Schematically, we have:

where stands for "feed-forward network". We can more succinctly write it aswith the implicit convention that the is applied to each row of the matrix individually.

The encoder layers are stacked. The first encoder layer takes the sequence of input vectors from the embedding layer, producing a sequence of vectors. This sequence of vectors is processed by the second encoder, and so on. The output from the final encoder layer is then used by the decoder.

As the encoder processes the entire input all at once, every token can attend to every other token (all-to-all attention), so there is no need for causal masking.

### Decoder

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=22)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/5/55/Transformer%2C_one_decoder_block.png/250px-Transformer%2C_one_decoder_block.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Transformer%2C_one_decoder_block.png/250px-Transformer%2C_one_decoder_block.png)

A decoder consists of an embedding layer, followed by multiple decoder layers, followed by an un-embedding layer.

Each decoder consists of three major components: a causally masked self-attention mechanism, a cross-attention mechanism, and a feed-forward neural network. The decoder functions in a similar fashion to the encoder, but an additional attention mechanism is inserted which instead draws relevant information from the encodings generated by the encoders. This mechanism can also be called the *encoder–decoder attention*.[[1]](#cite_note-2017_Attention_Is_All_You_Need-1)[[54]](#cite_note-:1-56)

Like the first encoder, the first decoder takes positional information and embeddings of the output sequence as its input, rather than encodings. The transformer must not use the current or future output to predict an output, so the output sequence must be partially masked to prevent this reverse information flow. [1] This allows for

[autoregressive](/wiki/Autoregressive_model)text generation. For decoding, all-to-all attention is inappropriate, because a token cannot attend to tokens not yet generated. Thus, the self-attention module in the decoder is causally masked.

In contrast, the cross-attention mechanism attends to the output vectors of the encoder, which is computed before the decoder starts decoding. Consequently, there is no need for masking in the cross-attention mechanism.

Schematically, we have:where is the matrix with rows being the output vectors from the encoder.

The last decoder is followed by a final un-embedding layer to produce the output probabilities over the vocabulary. Then, one of the tokens is sampled according to the probability, and the decoder can be run again to produce the next token, etc., autoregressively generating output text.

### Adapted architectures

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=23)]

Many [large language models](/wiki/Large_language_models), since they do not need to predict a whole new sequence from an input sequence, only use the encoder or decoder of the original transformer architecture. Early [GPT](/wiki/Generative_pre-trained_transformer) models are decoder-only models trained to predict the next token in a sequence.[[58]](#cite_note-gpt1paper-60)[BERT](/wiki/BERT_(language_model)), another language model, only makes use of an encoder, and is trained to predict a randomly masked token in a sequence.[[35]](#cite_note-:03-37)

## Full transformer architecture

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=24)]

### Sublayers

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=25)]

![](//upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Transformer%2C_stacked_multilayers.png/250px-Transformer%2C_stacked_multilayers.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Transformer%2C_stacked_multilayers.png/250px-Transformer%2C_stacked_multilayers.png)

Each encoder layer contains 2 sublayers: the self-attention and the feedforward network. Each decoder layer contains 3 sublayers: the causally masked self-attention, the cross-attention, and the feedforward network.

![](//upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Transformer_encoder%2C_with_norm-first_and_norm-last.png/250px-Transformer_encoder%2C_with_norm-first_and_norm-last.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Transformer_encoder%2C_with_norm-first_and_norm-last.png/250px-Transformer_encoder%2C_with_norm-first_and_norm-last.png)

![](//upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Transformer_decoder%2C_with_norm-first_and_norm-last.png/250px-Transformer_decoder%2C_with_norm-first_and_norm-last.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Transformer_decoder%2C_with_norm-first_and_norm-last.png/250px-Transformer_decoder%2C_with_norm-first_and_norm-last.png)

![](//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/250px-Transformer%2C_full_architecture.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/250px-Transformer%2C_full_architecture.png)

![](//upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Transformer%2C_schematic_object_hierarchy%2C_for_implementation_in_object-oriented_programming.png/250px-Transformer%2C_schematic_object_hierarchy%2C_for_implementation_in_object-oriented_programming.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Transformer%2C_schematic_object_hierarchy%2C_for_implementation_in_object-oriented_programming.png/250px-Transformer%2C_schematic_object_hierarchy%2C_for_implementation_in_object-oriented_programming.png)

[object hierarchy](/wiki/Object_hierarchy)for the full transformer architecture, in

[object-oriented programming](/wiki/Object-oriented_programming)style

The final points of detail are the [residual connections](/wiki/Residual_neural_network) and [layer normalization](/wiki/Layer_normalization), (denoted as "LayerNorm", or "LN" in the following), which while conceptually unnecessary, are necessary for numerical stability and convergence.

The residual connection, which is introduced to avoid vanishing gradient issues and stabilize the training process, can be expressed as follows: y = F(x) + x. The expression indicates that an output y is the sum of the transformation of input x (F(x)) and the input itself (x). Adding the input x can preserve the input information and avoid issues when the gradient of F(x) is close to zero.

Similarly to how the feedforward network modules are applied individually to each vector, the LayerNorm is also applied individually to each vector.

There are two common conventions in use: the *post-LN* and the *pre-LN* convention. In the post-LN convention, the output of each sublayer is where is the function implemented by the sublayer itself.

In the pre-LN convention, the output of each sublayer isThe original 2017 transformer used the post-LN convention. It was difficult to train and required careful hyperparameter tuning and a "warm-up" in learning rate, where it starts small and gradually increases. The pre-LN convention, proposed several times in 2018, [59] was found to be easier to train, requiring no warm-up, leading to faster convergence.


[[46]](#cite_note-auto1-48)### Pseudocode

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=26)]

The following is the pseudocode for a standard pre-LN encoder–decoder transformer, adapted from *Formal Algorithms for Transformers*[[60]](#cite_note-62)

input:Encoder input t_e Decoder input t_doutput:Array of probability distributions, with shape (decoder vocabulary size x length(decoder output sequence)) /* encoder */ z_e ← encoder.tokenizer(t_e)foreachtin1:length(z_e)doz_e[t] ← encoder.embedding(z_e[t]) + encoder.positional_embedding(t)foreachlin1:length(encoder.layers)dolayer ← encoder.layers[l] /* first sublayer */ z_e_copy ← copy(z_e)for eachtin1:length(z_e)doz_e[t] ← layer.layer_norm(z_e[t]) z_e ← layer.multihead_attention(z_e, z_e, z_e)for eachtin1:length(z_e)doz_e[t] ← z_e[t] + z_e_copy[t] /* second sublayer */ z_e_copy ← copy(z_e)for eachtin1:length(z_e)doz_e[t] ← layer.layer_norm(z_e[t]) z_e ← layer.feedforward(z_e)for eachtin1:length(z_e)doz_e[t] ← z_e[t] + z_e_copy[t]for eachtin1:length(z_e)doz_e[t] ← encoder.final_layer_norm(z_e[t]) /* decoder */ z_d ← decoder.tokenizer(t_d)foreachtin1:length(z_d)doz_d[t] ← decoder.embedding(z_d[t]) + decoder.positional_embedding(t)foreachlin1:length(decoder.layers)dolayer ← decoder.layers[l] /* first sublayer */ z_d_copy ← copy(z_d)for eachtin1:length(z_d)doz_d[t] ← layer.layer_norm(z_d[t]) z_d ← layer.masked_multihead_attention(z_d, z_d, z_d)for eachtin1:length(z_d)doz_d[t] ← z_d[t] + z_d_copy[t] /* second sublayer */ z_d_copy ← copy(z_d)for eachtin1:length(z_d)doz_d[t] ← layer.layer_norm(z_d[t]) z_d ← layer.multihead_attention(z_d, z_e, z_e)for eachiin1:length(z_d)doz_d[t] ← z_d[t] + z_d_copy[t] /* third sublayer */ z_d_copy ← copy(z_d)for eachtin1:length(z_d)doz_d[t] ← layer.layer_norm(z_d[t]) z_d ← layer.feedforward(z_d)for eachtin1:length(z_d)doz_d[t] ← z_d[t] + z_d_copy[t] z_d ← decoder.final_layer_norm(z_d) output_distributions ← []for eachtin1:length(z_d)dooutput_distributions.append(decoder.unembed(z_d[t]))returnoutput_distributions

### Terminology

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=27)]

The transformer architecture, being modular, allows variations. Several common variations are described here.[[61]](#cite_note-:3-63)

An "encoder-only" transformer applies the encoder to map an input text into a sequence of vectors that represent the input text. This is usually used for text embedding and [representation learning](/wiki/Feature_learning) for downstream applications. [BERT](/wiki/BERT_(language_model)) is encoder-only. They are less often used currently, as they were found to be not significantly better than training an encoder–decoder transformer, then taking just the encoder.[[51]](#cite_note-:4-53)

A "decoder-only" transformer is not literally decoder-only, since without an encoder, the cross-attention mechanism has nothing to attend to. Thus, the decoder layers in a decoder-only transformer is composed of just two sublayers: the causally masked self-attention, and the feedforward network. This is usually used for [text generation](/wiki/Natural_language_generation) and [instruction following](/wiki/Large_language_model#Instruction_tuning). The models in the [GPT series](/wiki/Generative_pre-trained_transformer) and [Chinchilla series](/wiki/Chinchilla_(language_model)) are decoder-only.

An "encoder–decoder" transformer is generally the same as the original transformer, with 2 sublayers per encoder layer and 3 sublayers per decoder layer, etc. They might have minor architectural improvements, such as [alternative activation functions](#Alternative_activation_functions), [changing the location of normalization](#pre-LN), etc. This is also usually used for text generation and instruction following. The models in the [T5 series](/wiki/T5_(language_model)) are encoder–decoder.[[61]](#cite_note-:3-63)

A "prefixLM" (prefix language model) is a decoder-only architecture, but with prefix masking, which is different from causal masking. Specifically, it has mask of the form[[61]](#cite_note-:3-63): Figure 3 where the first columns correspond to the "prefix", and the subsequent columns correspond to the autoregressively generated text based on the prefix. They resemble encoder–decoder models, but has less "sparsity". Such models are rarely used, though they are cited as theoretical possibilities and benchmarked comparisons.[[51]](#cite_note-:4-53)

There are also mixed seq2seq models. For example, in 2020, Google Translate replaced the previous RNN-encoder–RNN-decoder model with a transformer-encoder–RNN-decoder model, as transformer-based decoders did not appear to significantly increase quality unlike the encoder, while the RNN decoder was much faster.[[37]](#cite_note-gtrans-39)

## Subsequent work

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=28)]

### Alternative activation functions

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=29)]

The original transformer uses [ReLU](/wiki/ReLU) [activation function](/wiki/Activation_function). Other activation functions were developed. The [Llama series](/wiki/Llama_(language_model)) and [PaLM](/wiki/PaLM) used SwiGLU; [62] both GPT-1 and BERT

used GELU.

[[35]](#cite_note-:03-37)

[[63]](#cite_note-65)Alternative activation functions are often used in combination with [Gated Linear Units](/wiki/Gated_Linear_Unit) in the feedforward module.[[62]](#cite_note-:14-64)

### Alternative normalizations

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=30)]

The normalization used in the transformer can be different from LayerNorm. One example is [RMSNorm](/wiki/RMSNorm) [64] which is used in the

[Llama series](/wiki/Llama_(language_model)). Other examples include CapsuleNorm

ScaleNorm,

[[65]](#cite_note-67)or FixNorm.

[[66]](#cite_note-:9-68)

[[66]](#cite_note-:9-68)### Alternative positional encodings

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=31)]

Transformers may use other positional encoding methods than sinusoidal.[[67]](#cite_note-69)

The original transformer paper reported using a learned positional encoding, [68] but finding it not superior to the sinusoidal one.

Later,

[[1]](#cite_note-2017_Attention_Is_All_You_Need-1)found that causal masking itself provides enough signal to a transformer decoder that it can learn to implicitly perform absolute positional encoding without the positional encoding module.

[[69]](#cite_note-71)#### RoPE

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=32)]

RoPE (rotary positional embedding), [70] is best explained by considering a list of 2-dimensional vectors . Now pick some angle . Then RoPE encoding isEquivalently, if we write the 2-dimensional vectors as complex numbers , then RoPE encoding is just multiplication by an angle:For a list of -dimensional vectors, a RoPE encoder is defined by a sequence of angles . Then the RoPE encoding is applied to each pair of coordinates.

The benefit of RoPE is that the dot-product between two vectors depends on their relative location only: for any integer .

#### ALiBi

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=33)]

ALiBi (Attention with Linear Biases) [71] is not a

*replacement*for the positional encoder on the original transformer. Instead, it is an

*additional*positional encoder that is directly plugged into the attention mechanism. Specifically, the ALiBi attention mechanism isHere, is a real number ("scalar"), and is the

*linear bias*matrix defined byin other words, . The idea being that the linear bias matrix is a softened mask. Just as represent full attention paid, and represents no attention paid, the linear bias matrix increases attention paid in one direction and decreases attention paid in the other direction.

ALiBi allows pretraining on short context windows, then fine-tuning on longer context windows. Since it is directly plugged into the attention mechanism, it can be combined with any positional encoder that is plugged into the "bottom" of the entire network (which is where the sinusoidal encoder on the original transformer, as well as RoPE and many others, are located).

#### Relative Position Encodings

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=34)]

Relative Position Encodings [72] is similar to ALiBi, but more generic:where is a

[Toeplitz matrix](/wiki/Toeplitz_matrix), that is, whenever . This is contrasted with the original sinusoidal positional encoding, which is an "absolute positional encoding".


[[73]](#cite_note-75)### Efficient implementation

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=35)]

The transformer model has been implemented in standard deep learning [frameworks](/wiki/Framework_(computer_science)) such as [TensorFlow](/wiki/TensorFlow) and [PyTorch](/wiki/PyTorch). *Transformers* is a library produced by [Hugging Face](/wiki/Hugging_Face) that supplies transformer-based architectures and pretrained models.[[11]](#cite_note-wolf2020-11)

#### KV caching

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=36)]

When an autoregressive transformer is used for inference, such as generating text, the query vector is different at each step, but the already-computed key and value vectors are always the same. The **KV caching** method saves the computed key and value vectors at each attention block, so that they are not recomputed at each new token. **PagedAttention** applies [memory paging](/wiki/Memory_paging) to KV caching.[[74]](#cite_note-76)[[75]](#cite_note-77)[[76]](#cite_note-78)

If a transformer is used with a baked-in prompt, such as ["You are a customer support agent..."], then the key and value vectors can be computed for the prompt, and saved on disk. The saving in compute is significant when the model is used for many short real-time interactions, such as in online chatbots.

#### FlashAttention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=37)]

FlashAttention [77] is an algorithm that implements the transformer attention mechanism efficiently on a

[GPU](/wiki/Graphics_processing_unit). It is a communication-avoiding algorithm that performs

[matrix multiplications in blocks](/wiki/Block_matrix#Block_matrix_operations), such that each block fits within the

[cache](/wiki/Cache_(computing))of a GPU, and by careful management of the blocks it minimizes data copying between GPU caches (as data movement is slow). See the page on

[softmax](/wiki/Softmax_function#Numerical_algorithms)for details.

An improved version, FlashAttention-2,[[78]](#cite_note-80)[[79]](#cite_note-81) [80] was developed to cater to the rising demand for language models capable of handling longer context lengths. It offers enhancements in work partitioning and parallelism, enabling it to achieve up to 230 TFLOPs/s on

[A100](/wiki/Nvidia_A100)GPUs (

[FP16](/wiki/FP16)/

[BF16](/wiki/BF16)), a 2x speed increase over the original FlashAttention.

Key advancements in FlashAttention-2 include the reduction of non-matmul FLOPs, improved parallelism over the sequence length dimension, better work partitioning between GPU warps, and added support for head dimensions up to 256 and multi-query attention (MQA) and grouped-query attention (GQA).[[81]](#cite_note-83)

Benchmarks revealed FlashAttention-2 to be up to 2x faster than FlashAttention and up to 9x faster than a standard attention implementation in PyTorch. Future developments include optimization for new hardware like [H100](/wiki/Nvidia_H100) GPUs and new data types like [FP8](/wiki/Floating-point_arithmetic).

FlashAttention-4 focuses on [pipelining](/wiki/Pipeline_(Unix)) to increase instruction [throughput](/wiki/Network_throughput), and was developed to perform particularly well on [Blackwell GPUs](/wiki/Blackwell_(microarchitecture)).[[82]](#cite_note-84)

#### Multi-Query Attention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=38)]


![](//upload.wikimedia.org/wikipedia/commons/thumb/8/83/DeepSeek_KV_cache_comparison_between_MHA%2C_GQA%2C_MQA%2C_MLA.svg/250px-DeepSeek_KV_cache_comparison_between_MHA%2C_GQA%2C_MQA%2C_MLA.svg.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/8/83/DeepSeek_KV_cache_comparison_between_MHA%2C_GQA%2C_MQA%2C_MLA.svg/250px-DeepSeek_KV_cache_comparison_between_MHA%2C_GQA%2C_MQA%2C_MLA.svg.png)

Multi-Query Attention changes the Multihead Attention mechanism. [83] Whereas normally,

with Multi-Query Attention, there is just one , thus:


This has a neutral effect on model quality and training speed, but increases inference speed.

More generally, grouped-query attention (GQA) partitions attention heads into groups, each of which shares the key-value pair. MQA is GQA with one group, while standard Multihead Attention is GQA with the maximal number of groups.[[84]](#cite_note-86)

![](//upload.wikimedia.org/wikipedia/commons/thumb/2/20/DeepSeek_MoE_and_MLA_%28DeepSeek-V2%29.svg/250px-DeepSeek_MoE_and_MLA_%28DeepSeek-V2%29.svg.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/2/20/DeepSeek_MoE_and_MLA_%28DeepSeek-V2%29.svg/250px-DeepSeek_MoE_and_MLA_%28DeepSeek-V2%29.svg.png)

[mixture of experts](/wiki/Mixture_of_experts)


[[85]](#cite_note-:73-87): Figure 2

Multihead Latent Attention (MLA) is a [low-rank approximation](/wiki/Low-rank_approximation) to standard MHA. Specifically, each hidden vector, before entering the attention mechanism, is first projected to two low-dimensional spaces ("latent space"), one for query and one for key-value (KV vector). This design minimizes the KV cache, as only the low-dimensional KV vector needs to be cached.[[85]](#cite_note-:73-87)

#### Speculative decoding

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=39)]

Speculative decoding[[86]](#cite_note-:2-88) [87] is a method to accelerate token decoding. Similarly to

[speculative execution](/wiki/Speculative_execution)in CPUs, future tokens are computed quickly, then verified. If the quickly computed tokens are incorrect, they are discarded and computed slowly.

The key factor in speculative decoding is that a transformer decoder can verify faster than it can decode, in the following sense.

Suppose we have two transformer models like GPT-3 and GPT-3-small, both with a context window size of 512. To generate an entire context window autoregressively with greedy decoding with GPT-3, it must be run for 512 times, each time generating a token , taking time . However, if we had some educated guess for the values of these tokens, we could verify all of them in parallel, in one run of the model, by checking that each is indeed the token with the largest log-likelihood in the -th output.

In speculative decoding, a smaller model or some other simple heuristic is used to generate a few speculative tokens that are subsequently verified by the larger model. For example, suppose we use GPT-3-small to generate four speculative tokens: . This only takes . These tokens are then run through the larger GPT-3 in one go. Suppose that and are verified by GPT-3 as what it would have picked, then those are kept, but is not, so are discarded, and GPT-3 is run on those. This would take , which might be shorter than .

For non-greedy decoding, similar ideas apply, except the speculative tokens are accepted or rejected stochastically, in a way that guarantees the final output distribution is the same as if speculative decoding was not used.[[86]](#cite_note-:2-88)[[88]](#cite_note-90)

![](//upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Multi-Token_Prediction_%28DeepSeek%29_01.svg/250px-Multi-Token_Prediction_%28DeepSeek%29_01.svg.png)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Multi-Token_Prediction_%28DeepSeek%29_01.svg/250px-Multi-Token_Prediction_%28DeepSeek%29_01.svg.png)

In Multi-Token Prediction, a single forward pass creates a final embedding vector, which then is un-embedded into a token probability. However, that vector can then be further processed by another transformer block to predict the *next* token, and so on for arbitrarily many steps into the future. This trades off accuracy for speed, since each new token costs just one more transformer block, rather than the entire stack.[[89]](#cite_note-91)[[90]](#cite_note-92)

### Sub-quadratic transformers

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=40)]

Training transformer-based architectures can be expensive, especially for long inputs. [91] Many methods have been developed to attempt to address the issue. In the image domain, Swin transformer is an efficient architecture that performs attention inside shifting windows.

In the audio domain, SepTr decouples the attention in time and frequency domains.

[[92]](#cite_note-94)

[[93]](#cite_note-95)*Long Range Arena*(2020)

is a standard benchmark for comparing the behavior of transformer architectures over long inputs.

[[94]](#cite_note-96)#### Alternative attention graphs

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=41)]

The standard attention graph is either all-to-all or causal, both of which scales as where is the number of tokens in a sequence.

Reformer (2020)[[91]](#cite_note-reformer-93) [95] reduces the computational load from to by using

[locality-sensitive hashing](/wiki/Locality-sensitive_hashing)and reversible layers.


[[96]](#cite_note-98)Sparse attention [97] uses attention graphs that grows slower than . For example, BigBird (2020)

uses random

[[98]](#cite_note-100)[small-world networks](/wiki/Small-world_network)which grows as .

Ordinary transformers require a memory size that is quadratic in the size of the context window. Attention-free transformers [99] reduce this to a linear dependence while still retaining the advantages of a transformer by linking the key to the value.

#### Random Feature Attention

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=42)]

Random Feature Attention (2021) [100] uses

[Fourier random features](/wiki/Radial_basis_function_kernel#Fourier_random_features):where are independent samples from the normal distribution . This choice of parameters satisfy , or Consequently, the one-headed attention, with one query, can be written as where . Similarly for multiple queries, and for multihead attention.

This approximation can be computed in linear time, as we can compute the matrix first, then multiply it with the query. In essence, we have managed to obtain a more precise version of Performer (2022) [101] uses the same Random Feature Attention, but are first independently sampled from the normal distribution , then they are

[Gram-Schmidt processed](/wiki/Gram%E2%80%93Schmidt_process).

### Multimodality

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=43)]

Transformers can also be used/adapted for modalities (input or output) beyond just text, usually by finding a way to "tokenize" the modality.

Multimodal models can either be trained from scratch, or by finetuning. A 2022 study found that transformers pretrained only on natural language can be finetuned on only 0.03% of parameters and become competitive with [LSTMs](/wiki/LSTMs) on a variety of logical and visual tasks, demonstrating [transfer learning](/wiki/Transfer_learning). [102] The LLaVA was a vision-language model composed of a language model (Vicuna-13B)

and a vision model (

[[103]](#cite_note-105)[ViT](/wiki/Vision_transformer)-L/14), connected by a linear layer. Only the linear layer is finetuned.


[[104]](#cite_note-106)[Vision transformers](/wiki/Vision_transformer) [41] adapt the transformer to computer vision by breaking down input images as a series of patches, turning them into vectors, and treating them like embedding vector of tokens in a standard transformer.

Conformer [42] and later

[Whisper](/wiki/Whisper_(speech_recognition_system))

follow the same pattern for

[[105]](#cite_note-Radford_Kim_Xu_Brockman_p.-107)[speech recognition](/wiki/Speech_recognition), first turning the speech signal into a

[spectrogram](/wiki/Spectrogram), which is then treated like an image, i.e. broken down into a series of patches, turned into vectors and treated like embedding vector of tokens in a standard transformer.

[Perceivers](/wiki/Perceiver)[[106]](#cite_note-perceiver2021-108) [107] are a variant of transformers designed for multimodality.

For image generation, notable architectures are [DALL-E 1](/wiki/DALL-E) (2021), Parti (2022), [108] Phenaki (2023),

and Muse (2023).

[[109]](#cite_note-:13-111)Unlike later models, DALL-E is not a

[[110]](#cite_note-:12-112)[diffusion model](/wiki/Diffusion_model). Instead, it uses a decoder-only transformer that autoregressively generates a text, followed by the token representation of an image, which is then converted by a

[variational autoencoder](/wiki/Variational_autoencoder)to an image.

Parti is an encoder–decoder transformer, where the encoder processes a text prompt, and the decoder generates a token representation of an image.

[[111]](#cite_note-113)Muse is an encoder-only transformer that is trained to predict masked image tokens from unmasked image tokens. During generation, all input tokens are masked, and the highest-confidence predictions are included for the next iteration, until all tokens are predicted.

[[112]](#cite_note-114)Phenaki is a text-to-video model. It is a bidirectional masked transformer conditioned on pre-computed text tokens. The generated tokens are then decoded to a video.

[[110]](#cite_note-:12-112)

[[109]](#cite_note-:13-111)## Applications

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=44)]

The transformer has had great success in [natural language processing](/wiki/Natural_language_processing) (NLP). Many [large language models](/wiki/Large_language_model) such as [GPT-2](/wiki/GPT-2), [GPT-3](/wiki/GPT-3), [GPT-4](/wiki/GPT-4), [Gemini](/wiki/Gemini_(chatbot)), AlbertAGPT, [Claude](/wiki/Anthropic#Claude), [BERT](/wiki/BERT_(language_model)), [Grok](/wiki/Grok_(chatbot)), [XLNet](/wiki/XLNet), [RoBERTa](/wiki/BERT_(language_model)#RoBERTa) and [ChatGPT](/wiki/ChatGPT) demonstrate the ability of transformers to perform a wide variety of NLP-related subtasks and their related real-world applications, including:

[machine translation](/wiki/Machine_translation)[time series](/wiki/Time_series)prediction[document summarization](/wiki/Automatic_summarization)[document generation](/wiki/Natural_language_generation)[named entity recognition](/wiki/Named-entity_recognition)(NER)[[113]](#cite_note-115)[writing computer code](/wiki/Computer_programming)based on requirements expressed in natural language.[speech-to-text](/wiki/Speech-to-text)

Beyond traditional NLP, the transformer architecture has had success in other applications, such as:

[biological sequence analysis](/wiki/Sequence_analysis)[video understanding](/wiki/Computer_vision)[protein folding](/wiki/Protein_structure_prediction)(such as[AlphaFold](/wiki/AlphaFold))[evaluating](/wiki/Evaluation_function)chess board positions. Using static evaluation alone (that is, with no[Minimax](/wiki/Minimax)search) transformer achieved an[Elo](/wiki/Elo_rating_system)of 2895, putting it at[grandmaster](/wiki/Grandmaster_(chess))level.[[10]](#cite_note-grandmaster-10)

## See also

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=45)]

[seq2seq](/wiki/Seq2seq)– Family of machine learning approaches[Perceiver](/wiki/Perceiver)– Variant of Transformer designed for multimodal data[Vision transformer](/wiki/Vision_transformer)– Machine learning model for vision processing[Large language model](/wiki/Large_language_model)– Type of machine learning model[BERT (language model)](/wiki/BERT_(language_model))– Series of language models developed by Google AI[Generative pre-trained transformer](/wiki/Generative_pre-trained_transformer)– Type of large language model[T5 (language model)](/wiki/T5_(language_model))– Series of large language models developed by Google AI

## Notes

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=46)]

[^](#cite_ref-13)[Gated recurrent units](/wiki/Gated_recurrent_units)(2014) further reduced its complexity.Some architectures, such as RWKV or state space models, avoid the issue.[^](#cite_ref-17)

## References

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=47)]

- ^
**a****b****c****d****e****f****g****h****i****j****k****l**[Vaswani, Ashish](/wiki/Ashish_Vaswani); Shazeer, Noam; Parmar, Niki; Uszkoreit, Jakob; Jones, Llion;[Gomez, Aidan N](/wiki/Aidan_Gomez); Kaiser, Łukasz; Polosukhin, Illia (2017).["Attention is All you Need"](https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf)(PDF).*Advances in Neural Information Processing Systems*.**30**. Curran Associates, Inc. [^](#cite_ref-lstm1997_2-0)[Hochreiter, Sepp](/wiki/Sepp_Hochreiter);[Schmidhuber, Jürgen](/wiki/J%C3%BCrgen_Schmidhuber)(1 November 1997). "Long Short-Term Memory".*Neural Computation*.**9**(8): 1735–1780.[doi](/wiki/Doi_(identifier)):[10.1162/neco.1997.9.8.1735](https://doi.org/10.1162%2Fneco.1997.9.8.1735).[ISSN](/wiki/ISSN_(identifier))[0899-7667](https://search.worldcat.org/issn/0899-7667).[PMID](/wiki/PMID_(identifier))[9377276](https://pubmed.ncbi.nlm.nih.gov/9377276).[S2CID](/wiki/S2CID_(identifier))[1915014](https://api.semanticscholar.org/CorpusID:1915014).- ^
**a****b**["Better Language Models and Their Implications"](https://openai.com/blog/better-language-models/).*OpenAI*. 2019-02-14.[Archived](https://web.archive.org/web/20201219132206/https://openai.com/blog/better-language-models/)from the original on 2020-12-19. Retrieved 2019-08-25. - ^
**a**Bahdanau; Cho, Kyunghyun; Bengio, Yoshua (September 1, 2014). "Neural Machine Translation by Jointly Learning to Align and Translate".**b**[arXiv](/wiki/ArXiv_(identifier)):[1409.0473](https://arxiv.org/abs/1409.0473)[[cs.CL](https://arxiv.org/archive/cs.CL)]. Luong, Minh-Thang; Pham, Hieu; Manning, Christopher D. (August 17, 2015). "Effective Approaches to Attention-based Neural Machine Translation".[^](#cite_ref-inventconfirm_5-0)[arXiv](/wiki/ArXiv_(identifier)):[1508.04025](https://arxiv.org/abs/1508.04025)[[cs.CL](https://arxiv.org/archive/cs.CL)].- ^
**a**Chen, Lili; Lu, Kevin; Rajeswaran, Aravind; Lee, Kimin; Grover, Aditya; Laskin, Michael; Abbeel, Pieter; Srinivas, Aravind; Mordatch, Igor (2021-06-24),**b***Decision Transformer: Reinforcement Learning via Sequence Modeling*,[arXiv](/wiki/ArXiv_(identifier)):[2106.01345](https://arxiv.org/abs/2106.01345) Parisotto, Emilio; Song, Francis; Rae, Jack; Pascanu, Razvan; Gulcehre, Caglar; Jayakumar, Siddhant; Jaderberg, Max; Kaufman, Raphaël Lopez; Clark, Aidan; Noury, Seb; Botvinick, Matthew; Heess, Nicolas; Hadsell, Raia (2020-11-21).[^](#cite_ref-7)["Stabilizing Transformers for Reinforcement Learning"](https://proceedings.mlr.press/v119/parisotto20a.html).*Proceedings of the 37th International Conference on Machine Learning*. PMLR: 7487–7498.Radford, Alec; Jong Wook Kim; Xu, Tao; Brockman, Greg; McLeavey, Christine; Sutskever, Ilya (2022). "Robust Speech Recognition via Large-Scale Weak Supervision".[^](#cite_ref-Robust_Speech_Recognition_via_Large-Scale_Weak_Supervision_8-0)[arXiv](/wiki/ArXiv_(identifier)):[2212.04356](https://arxiv.org/abs/2212.04356)[[eess.AS](https://arxiv.org/archive/eess.AS)].Monastirsky, Maxim; Azulay, Osher; Sintov, Avishai (February 2023). "Learning to Throw With a Handful of Samples Using Decision Transformers".[^](#cite_ref-9)*IEEE Robotics and Automation Letters*.**8**(2): 576–583.[Bibcode](/wiki/Bibcode_(identifier)):[2023IRAL....8..576M](https://ui.adsabs.harvard.edu/abs/2023IRAL....8..576M).[doi](/wiki/Doi_(identifier)):[10.1109/LRA.2022.3229266](https://doi.org/10.1109%2FLRA.2022.3229266).[ISSN](/wiki/ISSN_(identifier))[2377-3766](https://search.worldcat.org/issn/2377-3766).- ^
**a**Ruoss, Anian; Delétang, Grégoire; Medapati, Sourabh; Grau-Moya, Jordi; Wenliang, Li; Catt, Elliot; Reid, John; Genewein, Tim (2024-02-07). "Grandmaster-Level Chess Without Search".**b**[arXiv](/wiki/ArXiv_(identifier)):[2402.04494v1](https://arxiv.org/abs/2402.04494v1)[[cs.LG](https://arxiv.org/archive/cs.LG)]. - ^
**a**Wolf, Thomas; Debut, Lysandre; Sanh, Victor; Chaumond, Julien; Delangue, Clement; Moi, Anthony; Cistac, Pierric; Rault, Tim; Louf, Remi; Funtowicz, Morgan; Davison, Joe; Shleifer, Sam; von Platen, Patrick; Ma, Clara; Jernite, Yacine; Plu, Julien; Xu, Canwen; Le Scao, Teven; Gugger, Sylvain; Drame, Mariama; Lhoest, Quentin; Rush, Alexander (2020). "Transformers: State-of-the-Art Natural Language Processing".**b***Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations*. pp. 38–45.[doi](/wiki/Doi_(identifier)):[10.18653/v1/2020.emnlp-demos.6](https://doi.org/10.18653%2Fv1%2F2020.emnlp-demos.6).[S2CID](/wiki/S2CID_(identifier))[208117506](https://api.semanticscholar.org/CorpusID:208117506). - ^
**a****b****c**["Open Sourcing BERT: State-of-the-Art Pre-training for Natural Language Processing"](http://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html).*Google AI Blog*. 2 November 2018.[Archived](https://web.archive.org/web/20210113211449/https://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html)from the original on 2021-01-13. Retrieved 2019-08-25. Feldman, J. A.; Ballard, D. H. (1982-07-01).[^](#cite_ref-14)["Connectionist models and their properties"](https://www.sciencedirect.com/science/article/pii/S0364021382800013).*Cognitive Science*.**6**(3): 205–254.[doi](/wiki/Doi_(identifier)):[10.1016/S0364-0213(82)80001-3](https://doi.org/10.1016%2FS0364-0213%2882%2980001-3).[ISSN](/wiki/ISSN_(identifier))[0364-0213](https://search.worldcat.org/issn/0364-0213).Rumelhart, David E.; McClelland, James L.; Hinton, Geoffrey E. (1987-07-29).[^](#cite_ref-PDP_15-0)(PDF). Cambridge, Mass: Bradford Books.*Parallel Distributed Processing, Volume 1: Explorations in the Microstructure of Cognition: Foundations, Chapter 2*[ISBN](/wiki/ISBN_(identifier))[978-0-262-68053-0](/wiki/Special:BookSources/978-0-262-68053-0).Giles, C. Lee; Maxwell, Tom (1987-12-01).[^](#cite_ref-16)["Learning, invariance, and generalization in high-order neural networks"](https://opg.optica.org/abstract.cfm?URI=ao-26-23-4972).*Applied Optics*.**26**(23): 4972–4978.[doi](/wiki/Doi_(identifier)):[10.1364/AO.26.004972](https://doi.org/10.1364%2FAO.26.004972).[ISSN](/wiki/ISSN_(identifier))[0003-6935](https://search.worldcat.org/issn/0003-6935).[PMID](/wiki/PMID_(identifier))[20523475](https://pubmed.ncbi.nlm.nih.gov/20523475).- ^
**a****b**[Schmidhuber, Jürgen](/wiki/J%C3%BCrgen_Schmidhuber)(1992).["Learning to control fast-weight memories: an alternative to recurrent nets"](https://archive.org/download/wikipedia-scholarly-sources-corpus/10.1162.zip/10.1162%252Fneco.1992.4.1.131.pdf)(PDF).*Neural Computation*.**4**(1): 131–139.[doi](/wiki/Doi_(identifier)):[10.1162/neco.1992.4.1.131](https://doi.org/10.1162%2Fneco.1992.4.1.131).[S2CID](/wiki/S2CID_(identifier))[16683347](https://api.semanticscholar.org/CorpusID:16683347). Christoph von der Malsburg: The correlation theory of brain function. Internal Report 81-2, MPI Biophysical Chemistry, 1981.[^](#cite_ref-malsburg1981_19-0)[http://cogprints.org/1380/1/vdM_correlation.pdf](http://cogprints.org/1380/1/vdM_correlation.pdf)See Reprint in Models of Neural Networks II, chapter 2, pages 95–119. Springer, Berlin, 1994.Jerome A. Feldman, "Dynamic connections in neural networks," Biological Cybernetics, vol. 46, no. 1, pp. 27–39, Dec. 1982.[^](#cite_ref-feldman1982_20-0)Hinton, Geoffrey E.; Plaut, David C. (1987).[^](#cite_ref-21)["Using Fast Weights to Deblur Old Memories"](https://escholarship.org/uc/item/0570j1dp).*Proceedings of the Annual Meeting of the Cognitive Science Society*.**9**.Katharopoulos, Angelos; Vyas, Apoorv; Pappas, Nikolaos; Fleuret, François (2020).[^](#cite_ref-fastlinear20202_22-0)["Transformers are RNNs: Fast autoregressive Transformers with linear attention"](https://proceedings.mlr.press/v119/katharopoulos20a.html).*ICML 2020*. PMLR. pp. 5156–5165.Schlag, Imanol; Irie, Kazuki;[^](#cite_ref-schlag20212_23-0)[Schmidhuber, Jürgen](/wiki/Juergen_Schmidhuber)(2021). "Linear Transformers Are Secretly Fast Weight Programmers".*ICML 2021*. Springer. pp. 9355–9366.- ^
**a**Cho, Kyunghyun; van Merriënboer, Bart; Gulcehre, Caglar; Bahdanau, Dzmitry; Bougares, Fethi; Schwenk, Holger; Bengio, Yoshua (October 2014).**b**["Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation"](https://aclanthology.org/D14-1179). In Moschitti, Alessandro; Pang, Bo; Daelemans, Walter (eds.).*Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)*. Doha, Qatar: Association for Computational Linguistics. pp. 1724–1734.[arXiv](/wiki/ArXiv_(identifier)):[1406.1078](https://arxiv.org/abs/1406.1078).[doi](/wiki/Doi_(identifier)):[10.3115/v1/D14-1179](https://doi.org/10.3115%2Fv1%2FD14-1179). - ^
**a**Sutskever, Ilya; Vinyals, Oriol; Le, Quoc Viet (14 Dec 2014). "Sequence to sequence learning with neural networks".**b**[arXiv](/wiki/ArXiv_(identifier)):[1409.3215](https://arxiv.org/abs/1409.3215)[[cs.CL](https://arxiv.org/archive/cs.CL)]. [first version posted to arXiv on 10 Sep 2014] Chung, Junyoung; Gulcehre, Caglar; Cho, KyungHyun; Bengio, Yoshua (2014). "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling".[^](#cite_ref-MyUser_Arxiv.org_May_18_2016c_26-0)[arXiv](/wiki/ArXiv_(identifier)):[1412.3555](https://arxiv.org/abs/1412.3555)[[cs.NE](https://arxiv.org/archive/cs.NE)].Gruber, N.; Jockisch, A. (2020), "Are GRU cells more specific and LSTM cells more sensitive in motive classification of text?",[^](#cite_ref-gruber_jockisch_27-0)*Frontiers in Artificial Intelligence*,**3**40,[doi](/wiki/Doi_(identifier)):[10.3389/frai.2020.00040](https://doi.org/10.3389%2Ffrai.2020.00040),[PMC](/wiki/PMC_(identifier))[7861254](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7861254),[PMID](/wiki/PMID_(identifier))[33733157](https://pubmed.ncbi.nlm.nih.gov/33733157),[S2CID](/wiki/S2CID_(identifier))[220252321](https://api.semanticscholar.org/CorpusID:220252321)Sutskever, Ilya; Vinyals, Oriol; Le, Quoc V (2014).[^](#cite_ref-28)["Sequence to Sequence Learning with Neural Networks"](https://proceedings.neurips.cc/paper/2014/hash/a14ac55a4f27472c5d894ec1c3c743d2-Abstract.html).*Advances in Neural Information Processing Systems*.**27**. Curran Associates, Inc.[arXiv](/wiki/ArXiv_(identifier)):[1409.3215](https://arxiv.org/abs/1409.3215).Luong, Minh-Thang; Pham, Hieu; Manning, Christopher D. (2015). "Effective Approaches to Attention-based Neural Machine Translation".[^](#cite_ref-29)[arXiv](/wiki/ArXiv_(identifier)):[1508.04025](https://arxiv.org/abs/1508.04025)[[cs.CL](https://arxiv.org/archive/cs.CL)].Wu, Yonghui; et al. (2016-09-01). "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation".[^](#cite_ref-Y4moj_30-0)[arXiv](/wiki/ArXiv_(identifier)):[1609.08144](https://arxiv.org/abs/1609.08144)[[cs.CL](https://arxiv.org/archive/cs.CL)].Lewis-Kraus, Gideon (2016-12-14).[^](#cite_ref-UJDu8_31-0)["The Great A.I. Awakening"](https://web.archive.org/web/20230524052626/https://www.nytimes.com/2016/12/14/magazine/the-great-ai-awakening.html).*The New York Times*.[ISSN](/wiki/ISSN_(identifier))[0362-4331](https://search.worldcat.org/issn/0362-4331). Archived from[the original](https://www.nytimes.com/2016/12/14/magazine/the-great-ai-awakening.html)on 24 May 2023. Retrieved 2023-06-22.Parikh, Ankur P.; Täckström, Oscar; Das, Dipanjan; Uszkoreit, Jakob (2016-09-25). "A Decomposable Attention Model for Natural Language Inference".[^](#cite_ref-32)[arXiv](/wiki/ArXiv_(identifier)):[1606.01933](https://arxiv.org/abs/1606.01933)[[cs.CL](https://arxiv.org/archive/cs.CL)].- ^
**a**Levy, Steven.**b**["8 Google Employees Invented Modern AI. Here's the Inside Story"](https://www.wired.com/story/eight-google-employees-invented-modern-ai-transformers-paper/).*Wired*.[ISSN](/wiki/ISSN_(identifier))[1059-1028](https://search.worldcat.org/issn/1059-1028).[Archived](https://web.archive.org/web/20240320101528/https://www.wired.com/story/eight-google-employees-invented-modern-ai-transformers-paper/)from the original on 20 Mar 2024. Retrieved 2024-08-06. Cheng, Jianpeng; Dong, Li; Lapata, Mirella (November 2016).[^](#cite_ref-34)["Long Short-Term Memory-Networks for Machine Reading"](https://aclanthology.org/D16-1053/). In Su, Jian; Duh, Kevin; Carreras, Xavier (eds.).*Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing*. Austin, Texas: Association for Computational Linguistics. pp. 551–561.[doi](/wiki/Doi_(identifier)):[10.18653/v1/D16-1053](https://doi.org/10.18653%2Fv1%2FD16-1053).Peng, Bo; Alcaide, Eric; Anthony, Quentin; Albalak, Alon; Arcadinho, Samuel; Biderman, Stella; Cao, Huanqi; Cheng, Xin; Chung, Michael (2023-12-10),[^](#cite_ref-35)*RWKV: Reinventing RNNs for the transformer Era*,[arXiv](/wiki/ArXiv_(identifier)):[2305.13048](https://arxiv.org/abs/2305.13048)Marche, Stephen (2024-08-23).[^](#cite_ref-36)["Was Linguistic A.I. Created by Accident?"](https://www.newyorker.com/science/annals-of-artificial-intelligence/was-linguistic-ai-created-by-accident).*The New Yorker*.[ISSN](/wiki/ISSN_(identifier))[0028-792X](https://search.worldcat.org/issn/0028-792X). Retrieved 2024-08-27.- ^
**a****b****c****d****e**Devlin, Jacob; Chang, Ming-Wei; Lee, Kenton; Toutanova, Kristina (11 October 2018). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding".**f**[arXiv](/wiki/ArXiv_(identifier)):[1810.04805v2](https://arxiv.org/abs/1810.04805v2)[[cs.CL](https://arxiv.org/archive/cs.CL)]. [^](#cite_ref-38)["Google: BERT now used on almost every English query"](https://searchengineland.com/google-bert-used-on-almost-every-english-query-342193).*Search Engine Land*. 2020-10-15. Retrieved 2020-11-24.- ^
**a**Caswell, Isaac; Liang, Bowen (June 8, 2020).**b**["Recent Advances in Google Translate"](https://research.google/blog/recent-advances-in-google-translate/).*Google Research*.[Archived](https://web.archive.org/web/20240704042433/https://research.google/blog/recent-advances-in-google-translate/)from the original on 4 Jul 2024. Retrieved 2024-08-07. [^](#cite_ref-40)["The inside story of how ChatGPT was built from the people who made it"](https://www.technologyreview.com/2023/03/03/1069311/inside-story-oral-history-how-chatgpt-built-openai/).*MIT Technology Review*. Retrieved 2024-08-06.[^](#cite_ref-gpt12_41-0)["Improving language understanding with unsupervised learning"](https://openai.com/research/language-unsupervised).*openai.com*. June 11, 2018.[Archived](https://web.archive.org/web/20230318210736/https://openai.com/research/language-unsupervised)from the original on 2023-03-18. Retrieved 2023-03-18.[^](#cite_ref-ngEG3_42-0), OpenAI, June 11, 2018, retrieved 2023-05-01*finetune-transformer-lm*- ^
**a**Dosovitskiy, Alexey; Beyer, Lucas; Kolesnikov, Alexander; Weissenborn, Dirk; Zhai, Xiaohua; Unterthiner, Thomas; Dehghani, Mostafa; Minderer, Matthias; Heigold, Georg; Gelly, Sylvain; Uszkoreit, Jakob (2021-06-03). "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale".**b**[arXiv](/wiki/ArXiv_(identifier)):[2010.11929](https://arxiv.org/abs/2010.11929)[[cs.CV](https://arxiv.org/archive/cs.CV)]. - ^
**a**Gulati, Anmol; Qin, James; Chiu, Chung-Cheng; Parmar, Niki; Zhang, Yu; Yu, Jiahui; Han, Wei; Wang, Shibo; Zhang, Zhengdong; Wu, Yonghui; Pang, Ruoming (2020). "Conformer: Convolution-augmented Transformer for Speech Recognition".**b**[arXiv](/wiki/ArXiv_(identifier)):[2005.08100](https://arxiv.org/abs/2005.08100)[[eess.AS](https://arxiv.org/archive/eess.AS)]. Choromanski, Krzysztof; Likhosherstov, Valerii; Dohan, David; Song, Xingyou; Gane, Andreea; Sarlos, Tamas; Hawkins, Peter; Davis, Jared; Mohiuddin, Afroz (2022-11-19),[^](#cite_ref-choromanski2020_45-0)*Rethinking Attention with Performers*,[arXiv](/wiki/ArXiv_(identifier)):[2009.14794](https://arxiv.org/abs/2009.14794)Liu, Zhuang; Mao, Hanzi; Wu, Chao-Yuan; Feichtenhofer, Christoph; Darrell, Trevor; Xie, Saining (2022).[^](#cite_ref-46). Conference on Computer Vision and Pattern Recognition (*A ConvNet for the 2020s*[CVPR](/wiki/CVPR)). pp. 11976–11986.Esser, Patrick; Kulal, Sumith; Blattmann, Andreas; Entezari, Rahim; Müller, Jonas; Saini, Harry; Levi, Yam; Lorenz, Dominik; Sauer, Axel (2024-03-05),[^](#cite_ref-:62_47-0)*Scaling Rectified Flow Transformers for High-Resolution Image Synthesis*,[arXiv](/wiki/ArXiv_(identifier)):[2403.03206](https://arxiv.org/abs/2403.03206)- ^
**a**Xiong, Ruibin; Yang, Yunchang; He, Di; Zheng, Kai; Zheng, Shuxin; Xing, Chen; Zhang, Huishuai; Lan, Yanyan; Wang, Liwei; Liu, Tie-Yan (2020-06-29). "On Layer Normalization in the Transformer Architecture".**b**[arXiv](/wiki/ArXiv_(identifier)):[2002.04745](https://arxiv.org/abs/2002.04745)[[cs.LG](https://arxiv.org/archive/cs.LG)]. Raffel, Colin; Shazeer, Noam; Roberts, Adam; Lee, Katherine; Narang, Sharan; Matena, Michael; Zhou, Yanqi; Li, Wei; Liu, Peter J. (2020-01-01).[^](#cite_ref-:0_49-0)["Exploring the limits of transfer learning with a unified text-to-text transformer"](https://dl.acm.org/doi/abs/10.5555/3455716.3455856).*The Journal of Machine Learning Research*.**21**(1): 140:5485–140:5551.[arXiv](/wiki/ArXiv_(identifier)):[1910.10683](https://arxiv.org/abs/1910.10683).[ISSN](/wiki/ISSN_(identifier))[1532-4435](https://search.worldcat.org/issn/1532-4435).Raffel, Colin; Shazeer, Noam; Roberts, Adam; Lee, Katherine; Narang, Sharan; Matena, Michael; Zhou, Yanqi; Li, Wei; Liu, Peter J. (2019). "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer".[^](#cite_ref-50)[arXiv](/wiki/ArXiv_(identifier)):[1910.10683](https://arxiv.org/abs/1910.10683)[[cs.LG](https://arxiv.org/archive/cs.LG)].- ^
**a****b**["Masked language modeling"](https://huggingface.co/docs/transformers/tasks/masked_language_modeling).*huggingface.co*. Retrieved 2023-10-05. - ^
**a****b**["Causal language modeling"](https://huggingface.co/docs/transformers/tasks/language_modeling).*huggingface.co*. Retrieved 2023-10-05. - ^
**a****b****c**Tay, Yi; Dehghani, Mostafa; Tran, Vinh Q.; Garcia, Xavier; Wei, Jason; Wang, Xuezhi; Chung, Hyung Won; Shakeri, Siamak; Bahri, Dara (2023-02-28),**d***UL2: Unifying Language Learning Paradigms*,[arXiv](/wiki/ArXiv_(identifier)):[2205.05131](https://arxiv.org/abs/2205.05131) Press, Ofir; Wolf, Lior (2017-02-21),[^](#cite_ref-54)*Using the Output Embedding to Improve Language Models*,[arXiv](/wiki/ArXiv_(identifier)):[1608.05859](https://arxiv.org/abs/1608.05859)Lintz, Nathan (2016-04-18).[^](#cite_ref-55)["Sequence Modeling with Neural Networks (Part 2): Attention Models"](https://indico.io/blog/sequence-modeling-neural-networks-part2-attention-models/).*Indico*.[Archived](https://web.archive.org/web/20201021203352/https://indico.io/blog/sequence-modeling-neural-networks-part2-attention-models/)from the original on 2020-10-21. Retrieved 2019-10-15.- ^
**a****b**Alammar, Jay.**c**["The Illustrated transformer"](http://jalammar.github.io/illustrated-transformer/).*jalammar.github.io*.[Archived](https://web.archive.org/web/20201018061610/https://jalammar.github.io/illustrated-transformer/)from the original on 2020-10-18. Retrieved 2019-10-15. Team, Keras.[^](#cite_ref-57)["Keras documentation: GPT2Backbone model"](https://keras.io/api/keras_nlp/models/gpt2/gpt2_backbone/).*keras.io*. Retrieved 2024-08-08.Clark, Kevin; Khandelwal, Urvashi; Levy, Omer; Manning, Christopher D. (August 2019).[^](#cite_ref-58)["What Does BERT Look at? An Analysis of BERT's Attention"](https://www.aclweb.org/anthology/W19-4828).*Proceedings of the 2019 ACL Workshop BlackboxNLP: Analyzing and Interpreting Neural Networks for NLP*. Florence, Italy: Association for Computational Linguistics: 276–286.[arXiv](/wiki/ArXiv_(identifier)):[1906.04341](https://arxiv.org/abs/1906.04341).[doi](/wiki/Doi_(identifier)):[10.18653/v1/W19-4828](https://doi.org/10.18653%2Fv1%2FW19-4828).[Archived](https://web.archive.org/web/20201021211357/https://www.aclweb.org/anthology/W19-4828/)from the original on 2020-10-21. Retrieved 2020-05-20.Yang, Zhilin; Dai, Zihang; Yang, Yiming; Carbonell, Jaime; Salakhutdinov, Russ R; Le, Quoc V (2019).[^](#cite_ref-59)["XLNet: Generalized Autoregressive Pretraining for Language Understanding"](https://proceedings.neurips.cc/paper/2019/hash/dc6a7e655d7e5840e66733e9ee67cc69-Abstract.html).*Advances in Neural Information Processing Systems*.**32**. Curran Associates, Inc.[arXiv](/wiki/ArXiv_(identifier)):[1906.08237](https://arxiv.org/abs/1906.08237).Radford, Alec; Narasimhan, Karthik; Salimans, Tim; Sutskever, Ilya (11 June 2018).[^](#cite_ref-gpt1paper_60-0)["Improving Language Understanding by Generative Pre-Training"](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf)(PDF).[OpenAI](/wiki/OpenAI). p. 12.[Archived](https://web.archive.org/web/20210126024542/https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf)(PDF) from the original on 26 January 2021. Retrieved 23 January 2021.Wang, Qiang; Li, Bei; Xiao, Tong; Zhu, Jingbo; Li, Changliang; Wong, Derek F.; Chao, Lidia S. (2019-06-04),[^](#cite_ref-61)*Learning Deep Transformer Models for Machine Translation*,[arXiv](/wiki/ArXiv_(identifier)):[1906.01787](https://arxiv.org/abs/1906.01787)Phuong, Mary; Hutter, Marcus (2022-07-19),[^](#cite_ref-62)*Formal Algorithms for Transformers*,[arXiv](/wiki/ArXiv_(identifier)):[2207.09238](https://arxiv.org/abs/2207.09238)- ^
**a****b**Raffel, Colin; Shazeer, Noam; Roberts, Adam; Lee, Katherine; Narang, Sharan; Matena, Michael; Zhou, Yanqi; Li, Wei; Liu, Peter J. (2020).**c**["Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer"](http://jmlr.org/papers/v21/20-074.html).*Journal of Machine Learning Research*.**21**(140): 1–67.[arXiv](/wiki/ArXiv_(identifier)):[1910.10683](https://arxiv.org/abs/1910.10683).[ISSN](/wiki/ISSN_(identifier))[1533-7928](https://search.worldcat.org/issn/1533-7928). - ^
**a**Shazeer, Noam (2020-02-01). "GLU Variants Improve Transformer".**b**[arXiv](/wiki/ArXiv_(identifier)):[2002.05202](https://arxiv.org/abs/2002.05202)[[cs.LG](https://arxiv.org/archive/cs.LG)]. Hendrycks, Dan; Gimpel, Kevin (2016-06-27). "Gaussian Error Linear Units (GELUs)".[^](#cite_ref-65)[arXiv](/wiki/ArXiv_(identifier)):[1606.08415v5](https://arxiv.org/abs/1606.08415v5)[[cs.LG](https://arxiv.org/archive/cs.LG)].Zhang, Biao; Sennrich, Rico (2019).[^](#cite_ref-66)["Root Mean Square Layer Normalization"](https://proceedings.neurips.cc/paper/2019/hash/1e8a19426224ca89e83cef47f1e7f53b-Abstract.html).*Advances in Neural Information Processing Systems*.**32**. Curran Associates, Inc.[arXiv](/wiki/ArXiv_(identifier)):[1910.07467](https://arxiv.org/abs/1910.07467).Tembine, Hamidou, Manzoor Ahmed Khan, and Issa Bamia. 2024. "Mean-Field-Type Transformers" Mathematics 12, no. 22: 3506.[^](#cite_ref-67)[https://doi.org/10.3390/math12223506](https://doi.org/10.3390/math12223506)- ^
**a**Nguyen, Toan Q.; Salazar, Julian (2019-11-02). Niehues, Jan; Cattoni, Rolando; Stüker, Sebastian; Negri, Matteo; Turchi, Marco; Ha, Thanh-Le; Salesky, Elizabeth; Sanabria, Ramon; Barrault, Loic (eds.).**b**["Transformers without Tears: Improving the Normalization of Self-Attention"](https://aclanthology.org/2019.iwslt-1.17).*Proceedings of the 16th International Conference on Spoken Language Translation*. Hong Kong: Association for Computational Linguistics.[arXiv](/wiki/ArXiv_(identifier)):[1910.05895](https://arxiv.org/abs/1910.05895).[doi](/wiki/Doi_(identifier)):[10.5281/zenodo.3525484](https://doi.org/10.5281%2Fzenodo.3525484). Dufter, Philipp; Schmitt, Martin; Schütze, Hinrich (2022-06-06).[^](#cite_ref-69)["Position Information in transformers: An Overview"](https://doi.org/10.1162%2Fcoli_a_00445).*Computational Linguistics*.**48**(3): 733–763.[arXiv](/wiki/ArXiv_(identifier)):[2102.11090](https://arxiv.org/abs/2102.11090).[doi](/wiki/Doi_(identifier)):[10.1162/coli_a_00445](https://doi.org/10.1162%2Fcoli_a_00445).[ISSN](/wiki/ISSN_(identifier))[0891-2017](https://search.worldcat.org/issn/0891-2017).[S2CID](/wiki/S2CID_(identifier))[231986066](https://api.semanticscholar.org/CorpusID:231986066).Gehring, Jonas; Auli, Michael; Grangier, David; Yarats, Denis; Dauphin, Yann N. (2017-07-17).[^](#cite_ref-70)["Convolutional Sequence to Sequence Learning"](https://proceedings.mlr.press/v70/gehring17a.html).*Proceedings of the 34th International Conference on Machine Learning*. PMLR: 1243–1252.Haviv, Adi; Ram, Ori; Press, Ofir; Izsak, Peter; Levy, Omer (2022-12-05),[^](#cite_ref-71)*Transformer Language Models without Positional Encodings Still Learn Positional Information*,[arXiv](/wiki/ArXiv_(identifier)):[2203.16634](https://arxiv.org/abs/2203.16634)Su, Jianlin; Lu, Yu; Pan, Shengfeng; Murtadha, Ahmed; Wen, Bo; Liu, Yunfeng (2021-04-01). "RoFormer: Enhanced Transformer with Rotary Position Embedding".[^](#cite_ref-72)[arXiv](/wiki/ArXiv_(identifier)):[2104.09864](https://arxiv.org/abs/2104.09864)[[cs.CL](https://arxiv.org/archive/cs.CL)].Press, Ofir; Smith, Noah A.; Lewis, Mike (2021-08-01). "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation".[^](#cite_ref-73)[arXiv](/wiki/ArXiv_(identifier)):[2108.12409](https://arxiv.org/abs/2108.12409)[[cs.CL](https://arxiv.org/archive/cs.CL)].Shaw, Peter; Uszkoreit, Jakob; Vaswani, Ashish (2018). "Self-Attention with Relative Position Representations".[^](#cite_ref-74)[arXiv](/wiki/ArXiv_(identifier)):[1803.02155](https://arxiv.org/abs/1803.02155)[[cs.CL](https://arxiv.org/archive/cs.CL)].Ke, Guolin; He, Di; Liu, Tie-Yan (2021-03-15),[^](#cite_ref-75)*Rethinking Positional Encoding in Language Pre-training*,[arXiv](/wiki/ArXiv_(identifier)):[2006.15595](https://arxiv.org/abs/2006.15595)Kwon, Woosuk; Li, Zhuohan; Zhuang, Siyuan; Sheng, Ying; Zheng, Lianmin; Yu, Cody Hao; Gonzalez, Joseph; Zhang, Hao; Stoica, Ion (2023-10-23).[^](#cite_ref-76)["Efficient Memory Management for Large Language Model Serving with PagedAttention"](https://dl.acm.org/doi/10.1145/3600006.3613165).*Proceedings of the 29th Symposium on Operating Systems Principles*. SOSP '23. New York, NY, USA: Association for Computing Machinery. pp. 611–626.[arXiv](/wiki/ArXiv_(identifier)):[2309.06180](https://arxiv.org/abs/2309.06180).[doi](/wiki/Doi_(identifier)):[10.1145/3600006.3613165](https://doi.org/10.1145%2F3600006.3613165).[ISBN](/wiki/ISBN_(identifier))[979-8-4007-0229-7](/wiki/Special:BookSources/979-8-4007-0229-7).[^](#cite_ref-77), vLLM, 2024-06-20, retrieved 2024-06-20*vllm-project/vllm*Zhuohan Li, Woosuk Kwon; Zhuang, Siyuan; Sheng, Ying; Zheng, Lianmin; Yu, Cody; Gonzalez, Joey; Zhang, Hao; Stoica, Ion (2023-06-20).[^](#cite_ref-78)["vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention"](https://blog.vllm.ai/2023/06/20/vllm.html).*vLLM Blog*. Retrieved 2024-06-20.Dao, Tri; Fu, Dan; Ermon, Stefano; Rudra, Atri; Ré, Christopher (2022-12-06).[^](#cite_ref-79)["FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html).*Advances in Neural Information Processing Systems*.**35**: 16344–16359.[arXiv](/wiki/ArXiv_(identifier)):[2205.14135](https://arxiv.org/abs/2205.14135).[^](#cite_ref-80)["Stanford CRFM"](https://crfm.stanford.edu/2023/07/17/flash2.html).*crfm.stanford.edu*. Retrieved 2023-07-18.[^](#cite_ref-81)["FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"](https://princeton-nlp.github.io/flash-atttention-2/).*Princeton NLP*. 2023-06-17. Retrieved 2023-07-18.[^](#cite_ref-82)["Introducing Together AI Chief Scientist Tri Dao, as he releases FlashAttention-2 to speed up model training and inference"](https://together.ai/blog/tri-dao-flash-attention).*TOGETHER*. Retrieved 2023-07-18.Ainslie, Joshua; Lee-Thorp, James; de Jong, Michiel; Zemlyanskiy, Yury; Lebrón, Federico; Sanghai, Sumit (2023-12-23). "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints".[^](#cite_ref-83)[arXiv](/wiki/ArXiv_(identifier)):[2305.13245](https://arxiv.org/abs/2305.13245)[[cs.CL](https://arxiv.org/archive/cs.CL)].[^](#cite_ref-84)["We reverse-engineered Flash Attention 4"](https://modal.com/blog/reverse-engineer-flash-attention-4).*Modal*. Retrieved 2025-09-26.Chowdhery, Aakanksha; Narang, Sharan; Devlin, Jacob; Bosma, Maarten; Mishra, Gaurav; Roberts, Adam; Barham, Paul; Chung, Hyung Won; Sutton, Charles; Gehrmann, Sebastian; Schuh, Parker; Shi, Kensen; Tsvyashchenko, Sasha; Maynez, Joshua; Rao, Abhishek (2022-04-01). "PaLM: Scaling Language Modeling with Pathways".[^](#cite_ref-85)[arXiv](/wiki/ArXiv_(identifier)):[2204.02311](https://arxiv.org/abs/2204.02311)[[cs.CL](https://arxiv.org/archive/cs.CL)].Ainslie, Joshua; Lee-Thorp, James; de Jong, Michiel; Zemlyanskiy, Yury; Lebrón, Federico; Sanghai, Sumit (2023-12-23),[^](#cite_ref-86)*GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*,[arXiv](/wiki/ArXiv_(identifier)):[2305.13245](https://arxiv.org/abs/2305.13245)- ^
**a**DeepSeek-AI; Liu, Aixin; Feng, Bei; Wang, Bin; Wang, Bingxuan; Liu, Bo; Zhao, Chenggang; Dengr, Chengqi; Ruan, Chong (19 June 2024),**b***DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model*,[arXiv](/wiki/ArXiv_(identifier)):[2405.04434](https://arxiv.org/abs/2405.04434). - ^
**a**Leviathan, Yaniv; Kalman, Matan; Matias, Yossi (2023-05-18),**b***Fast Inference from Transformers via Speculative Decoding*,[arXiv](/wiki/ArXiv_(identifier)):[2211.17192](https://arxiv.org/abs/2211.17192) Fu, Yao (2023-12-13).[^](#cite_ref-89)["Towards 100x Speedup: Full Stack Transformer Inference Optimization"](https://yaofu.notion.site/Towards-100x-Speedup-Full-Stack-Transformer-Inference-Optimization-43124c3688e14cffaf2f1d6cbdf26c6c).Chen, Charlie; Borgeaud, Sebastian; Irving, Geoffrey; Lespiau, Jean-Baptiste; Sifre, Laurent; Jumper, John (2023-02-02),[^](#cite_ref-90)*Accelerating Large Language Model Decoding with Speculative Sampling*,[arXiv](/wiki/ArXiv_(identifier)):[2302.01318](https://arxiv.org/abs/2302.01318)Gloeckle, Fabian; Badr Youbi Idrissi; Rozière, Baptiste; Lopez-Paz, David; Synnaeve, Gabriel (2024). "Better & Faster Large Language Models via Multi-token Prediction".[^](#cite_ref-91)[arXiv](/wiki/ArXiv_(identifier)):[2404.19737](https://arxiv.org/abs/2404.19737)[[cs.CL](https://arxiv.org/archive/cs.CL)].DeepSeek-AI; et al. (2024). "DeepSeek-V3 Technical Report".[^](#cite_ref-92)[arXiv](/wiki/ArXiv_(identifier)):[2412.19437](https://arxiv.org/abs/2412.19437)[[cs.CL](https://arxiv.org/archive/cs.CL)].- ^
**a**Kitaev, Nikita; Kaiser, Łukasz; Levskaya, Anselm (2020). "Reformer: The Efficient Transformer".**b**[arXiv](/wiki/ArXiv_(identifier)):[2001.04451](https://arxiv.org/abs/2001.04451)[[cs.LG](https://arxiv.org/archive/cs.LG)]. Liu, Ze; Lin, Yutong; Cao, Yue; Hu, Han; Wei, Yixuan; Zhang, Zheng; Lin, Stephen; Guo, Baining (2021). "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows".[^](#cite_ref-94)*2021 IEEE/CVF International Conference on Computer Vision (ICCV)*. IEEE. pp. 9992–10002.[arXiv](/wiki/ArXiv_(identifier)):[2103.14030](https://arxiv.org/abs/2103.14030).[doi](/wiki/Doi_(identifier)):[10.1109/ICCV48922.2021.00986](https://doi.org/10.1109%2FICCV48922.2021.00986).[ISBN](/wiki/ISBN_(identifier))[978-1-6654-2812-5](/wiki/Special:BookSources/978-1-6654-2812-5).Ristea, Nicolaea Catalin; Ionescu, Radu Tudor; Khan, Fahad Shahbaz (2022-09-18).[^](#cite_ref-95)["SepTr: Separable Transformer for Audio Spectrogram Processing"](https://www.isca-archive.org/interspeech_2022/ristea22_interspeech.html).*Interspeech*. ISCA: 4103–4107.[arXiv](/wiki/ArXiv_(identifier)):[2203.09581](https://arxiv.org/abs/2203.09581).[doi](/wiki/Doi_(identifier)):[10.21437/Interspeech.2022-249](https://doi.org/10.21437%2FInterspeech.2022-249).Tay, Yi; Dehghani, Mostafa; Abnar, Samira; Shen, Yikang; Bahri, Dara; Pham, Philip; Rao, Jinfeng; Yang, Liu; Ruder, Sebastian; Metzler, Donald (2020-11-08). "Long Range Arena: A Benchmark for Efficient Transformers".[^](#cite_ref-96)[arXiv](/wiki/ArXiv_(identifier)):[2011.04006](https://arxiv.org/abs/2011.04006)[[cs.LG](https://arxiv.org/archive/cs.LG)].[^](#cite_ref-97)["Reformer: The Efficient Transformer"](http://ai.googleblog.com/2020/01/reformer-efficient-transformer.html).*Google AI Blog*. 16 January 2020.[Archived](https://web.archive.org/web/20201022210019/https://ai.googleblog.com/2020/01/reformer-efficient-transformer.html)from the original on 2020-10-22. Retrieved 2020-10-22.Gomez, Aidan N; Ren, Mengye; Urtasun, Raquel; Grosse, Roger B (2017).[^](#cite_ref-98)["The Reversible Residual Network: Backpropagation Without Storing Activations"](https://proceedings.neurips.cc/paper/2017/hash/f9be311e65d81a9ad8150a60844bb94c-Abstract.html).*Advances in Neural Information Processing Systems*.**30**. Curran Associates, Inc.[arXiv](/wiki/ArXiv_(identifier)):[1707.04585](https://arxiv.org/abs/1707.04585).Child, Rewon; Gray, Scott; Radford, Alec; Sutskever, Ilya (2019-04-23),[^](#cite_ref-99)*Generating Long Sequences with Sparse Transformers*,[arXiv](/wiki/ArXiv_(identifier)):[1904.10509](https://arxiv.org/abs/1904.10509)[^](#cite_ref-100)["Constructing Transformers For Longer Sequences with Sparse Attention Methods"](https://ai.googleblog.com/2021/03/constructing-transformers-for-longer.html).*Google AI Blog*. 25 March 2021.[Archived](https://web.archive.org/web/20210918150757/https://ai.googleblog.com/2021/03/constructing-transformers-for-longer.html)from the original on 2021-09-18. Retrieved 2021-05-28.Zhai, Shuangfei; Talbott, Walter; Srivastava, Nitish; Huang, Chen; Goh, Hanlin; Zhang, Ruixiang; Susskind, Josh (2021-09-21). "An Attention Free Transformer".[^](#cite_ref-101)[arXiv](/wiki/ArXiv_(identifier)):[2105.14103](https://arxiv.org/abs/2105.14103)[[cs.LG](https://arxiv.org/archive/cs.LG)].Peng, Hao; Pappas, Nikolaos; Yogatama, Dani; Schwartz, Roy; Smith, Noah A.; Kong, Lingpeng (2021-03-19). "Random Feature Attention".[^](#cite_ref-102)[arXiv](/wiki/ArXiv_(identifier)):[2103.02143](https://arxiv.org/abs/2103.02143)[[cs.CL](https://arxiv.org/archive/cs.CL)].Choromanski, Krzysztof; Likhosherstov, Valerii; Dohan, David; Song, Xingyou; Gane, Andreea; Sarlos, Tamas; Hawkins, Peter; Davis, Jared; Belanger, David; Colwell, Lucy; Weller, Adrian (2020-09-30). "Masked Language Modeling for Proteins via Linearly Scalable Long-Context Transformers".[^](#cite_ref-103)[arXiv](/wiki/ArXiv_(identifier)):[2006.03555](https://arxiv.org/abs/2006.03555)[[cs.LG](https://arxiv.org/archive/cs.LG)].Lu, Kevin; Grover, Aditya; Abbeel, Pieter; Mordatch, Igor (2022-06-28).[^](#cite_ref-104)["Frozen Pretrained Transformers as Universal Computation Engines"](https://ojs.aaai.org/index.php/AAAI/article/view/20729).*Proceedings of the AAAI Conference on Artificial Intelligence*.**36**(7): 7628–7636.[doi](/wiki/Doi_(identifier)):[10.1609/aaai.v36i7.20729](https://doi.org/10.1609%2Faaai.v36i7.20729).[ISSN](/wiki/ISSN_(identifier))[2374-3468](https://search.worldcat.org/issn/2374-3468).[^](#cite_ref-105)["Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90%* ChatGPT Quality | LMSYS Org"](https://lmsys.org/blog/2023-03-30-vicuna).*lmsys.org*. Retrieved 2024-08-11.Liu, Haotian; Li, Chunyuan; Wu, Qingyang; Lee, Yong Jae (2023-12-15).[^](#cite_ref-106)["Visual Instruction Tuning"](https://proceedings.neurips.cc/paper_files/paper/2023/hash/6dcf277ea32ce3288914faf369fe6de0-Abstract-Conference.html).*Advances in Neural Information Processing Systems*.**36**: 34892–34916.Radford, Alec; Kim, Jong Wook; Xu, Tao; Brockman, Greg; McLeavey, Christine; Sutskever, Ilya (2022). "Robust Speech Recognition via Large-Scale Weak Supervision".[^](#cite_ref-Radford_Kim_Xu_Brockman_p._107-0)[arXiv](/wiki/ArXiv_(identifier)):[2212.04356](https://arxiv.org/abs/2212.04356)[[eess.AS](https://arxiv.org/archive/eess.AS)].Jaegle, Andrew; Gimeno, Felix; Brock, Andrew; Zisserman, Andrew; Vinyals, Oriol; Carreira, Joao (2021-06-22). "Perceiver: General Perception with Iterative Attention".[^](#cite_ref-perceiver2021_108-0)[arXiv](/wiki/ArXiv_(identifier)):[2103.03206](https://arxiv.org/abs/2103.03206)[[cs.CV](https://arxiv.org/archive/cs.CV)].Jaegle, Andrew; Borgeaud, Sebastian; Alayrac, Jean-Baptiste; Doersch, Carl; Ionescu, Catalin; Ding, David; Koppula, Skanda; Zoran, Daniel; Brock, Andrew; Shelhamer, Evan; Hénaff, Olivier (2021-08-02). "Perceiver IO: A General Architecture for Structured Inputs & Outputs".[^](#cite_ref-jaegle2021b_109-0)[arXiv](/wiki/ArXiv_(identifier)):[2107.14795](https://arxiv.org/abs/2107.14795)[[cs.LG](https://arxiv.org/archive/cs.LG)].[^](#cite_ref-110)["Parti: Pathways Autoregressive Text-to-Image Model"](https://sites.research.google/parti/).*sites.research.google*. Retrieved 2024-08-09.- ^
**a**Villegas, Ruben; Babaeizadeh, Mohammad; Kindermans, Pieter-Jan; Moraldo, Hernan; Zhang, Han; Saffar, Mohammad Taghi; Castro, Santiago; Kunze, Julius; Erhan, Dumitru (2022-09-29). "Phenaki: Variable Length Video Generation from Open Domain Textual Descriptions".**b**[arXiv](/wiki/ArXiv_(identifier)):[2210.02399](https://arxiv.org/abs/2210.02399)[[cs.CV](https://arxiv.org/archive/cs.CV)]. - ^
**a**Chang, Huiwen; Zhang, Han; Barber, Jarred; Maschinot, A. J.; Lezama, Jose; Jiang, Lu; Yang, Ming-Hsuan; Murphy, Kevin; Freeman, William T. (2023-01-02). "Muse: Text-To-Image Generation via Masked Generative Transformers".**b**[arXiv](/wiki/ArXiv_(identifier)):[2301.00704](https://arxiv.org/abs/2301.00704)[[cs.CV](https://arxiv.org/archive/cs.CV)]. Ramesh, Aditya; Pavlov, Mikhail; Goh, Gabriel; Gray, Scott; Voss, Chelsea; Radford, Alec; Chen, Mark; Sutskever, Ilya (2021-02-26),[^](#cite_ref-113)*Zero-Shot Text-to-Image Generation*,[arXiv](/wiki/ArXiv_(identifier)):[2102.12092](https://arxiv.org/abs/2102.12092)Yu, Jiahui; Xu, Yuanzhong; Koh, Jing Yu; Luong, Thang; Baid, Gunjan; Wang, Zirui; Vasudevan, Vijay; Ku, Alexander; Yang, Yinfei (2022-06-21),[^](#cite_ref-114)*Scaling Autoregressive Models for Content-Rich Text-to-Image Generation*,[arXiv](/wiki/ArXiv_(identifier)):[2206.10789](https://arxiv.org/abs/2206.10789)Kariampuzha, William; Alyea, Gioconda; Qu, Sue; Sanjak, Jaleal; Mathé, Ewy; Sid, Eric; Chatelaine, Haley; Yadaw, Arjun; Xu, Yanji; Zhu, Qian (2023).[^](#cite_ref-115)["Precision information extraction for rare disease epidemiology at scale"](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9972634).*Journal of Translational Medicine*.**21**(1): 157.[doi](/wiki/Doi_(identifier)):[10.1186/s12967-023-04011-y](https://doi.org/10.1186%2Fs12967-023-04011-y).[PMC](/wiki/PMC_(identifier))[9972634](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9972634).[PMID](/wiki/PMID_(identifier))[36855134](https://pubmed.ncbi.nlm.nih.gov/36855134).

## Further reading

[[edit](/w/index.php?title=Transformer_(deep_learning)&action=edit§ion=48)]

- Alexander Rush,
[The Annotated transformer](https://nlp.seas.harvard.edu/2018/04/03/attention.html)[Archived](https://web.archive.org/web/20210922093841/https://nlp.seas.harvard.edu/2018/04/03/attention.html)2021-09-22 at the[Wayback Machine](/wiki/Wayback_Machine), Harvard NLP group, 3 April 2018 - Phuong, Mary; Hutter, Marcus (2022). "Formal Algorithms for Transformers".
[arXiv](/wiki/ArXiv_(identifier)):[2207.09238](https://arxiv.org/abs/2207.09238)[[cs.LG](https://arxiv.org/archive/cs.LG)]. - Ferrando, Javier; Sarti, Gabriele; Bisazza, Arianna; Costa-jussà, Marta R. (2024-05-01). "A Primer on the Inner Workings of Transformer-based Language Models".
[arXiv](/wiki/ArXiv_(identifier)):[2405.00208](https://arxiv.org/abs/2405.00208)[[cs.CL](https://arxiv.org/archive/cs.CL)]. - Leech, Gavin (2024-11-06).
["Transformer++"](https://web.archive.org/web/20250226110336/https://www.gleech.org/tplus).*argmin gravitas*. Archived from[the original](https://www.gleech.org/tplus)on 2025-02-26. Retrieved 2025-05-08. - Kitamura, Felipe; Moreno Júdice de Mattos Farina, Eduardo; Pedro Mazuco, João; Moy, Linda; M. Prevedello, Luciano (2025-08-25).
["Texts Are More than Notes, They Are Data: A Glimpse into How Machines Understand Text"](https://pubs.rsna.org/doi/10.1148/radiol.243217).*Radiology*.**316**(2) e243217.[doi](/wiki/Doi_(identifier)):[10.1148/radiol.243217](https://doi.org/10.1148%2Fradiol.243217).[PMID](/wiki/PMID_(identifier))[40892454](https://pubmed.ncbi.nlm.nih.gov/40892454).