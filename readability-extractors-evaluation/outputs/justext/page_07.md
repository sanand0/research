A standard transformer architecture, showing on the left an encoder, and on the right a decoder. Note: it uses the pre-LN convention, which is different from the post-LN convention used in the original 2017 transformer.

In deep learning, the transformer is a neural network architecture based on the multi-head attention mechanism, in which text is converted to numerical representations called tokens, and each token is converted into a vector via lookup from a word embedding table.[1] At each layer, each token is then contextualized within the scope of the context window with other (unmasked) tokens via a parallel multi-head attention mechanism, allowing the signal for key tokens to be amplified and less important tokens to be diminished.

History

Predecessors

For many years, sequence modelling and generation was done by using plain recurrent neural networks (RNNs). A well-cited early example was the Elman network (1990). In theory, the information from one token can propagate arbitrarily far down the sequence, but in practice the vanishing-gradient problem leaves the model's state at the end of a long sentence without precise, extractable information about preceding tokens.

A key breakthrough was LSTM (1995),[note 1] an RNN which used various innovations to overcome the vanishing gradient problem, allowing efficient learning of long-sequence modelling. One key innovation was the use of an attention mechanism which used neurons that multiply the outputs of other neurons, so-called multiplicative units.[13] Neural networks using multiplicative units were later called sigma-pi networks[14] or higher-order networks.[15] LSTM became the standard architecture for long sequence modelling until the 2017 publication of transformers. However, LSTM still used sequential processing, like most other RNNs.[note 2] Specifically, RNNs operate one token at a time from first to last; they cannot operate in parallel over all tokens in a sequence.

Modern transformers overcome this problem, but unlike RNNs, they require computation time that is quadratic in the size of the context window. The linearly scaling fast weight controller (1992) learns to compute a weight matrix for further processing depending on the input.[16] One of its two networks has "fast weights" or "dynamic links" (1981).[17][18][19] A slow neural network learns by gradient descent to generate keys and values for computing the weight changes of the fast neural network which computes answers to queries.[16] This was later shown to be equivalent to the unnormalized linear transformer.[20][21]

Attention with seq2seq

The idea of encoder–decoder sequence transduction had been developed in the early 2010s; commonly cited as the originators that produced seq2seq are two concurrently published papers from 2014.[22][23]

A 380M-parameter model for machine translation uses two long short-term memories (LSTM).[23] Its architecture consists of two parts. The encoder is an LSTM that takes in a sequence of tokens and turns it into a vector. The decoder is another LSTM that converts the vector into a sequence of tokens. Similarly, another 130M-parameter model used gated recurrent units (GRU) instead of LSTM.[22] Later research showed that GRUs are neither better nor worse than LSTMs for seq2seq.[24][25]

These early seq2seq models had no attention mechanism, and the state vector is accessible only after the last word of the source text was processed. Although in theory such a vector retains the information about the whole original sentence, in practice the information is poorly preserved. This is because the input is processed sequentially by one recurrent network into a fixed-size output vector, which is then processed by another recurrent network into an output. If the input is long, then the output vector would not be able to contain all relevant information, degrading the output. As evidence, reversing the input sentence improved seq2seq translation.[26]

The RNN search model introduced an attention mechanism to seq2seq for machine translation to solve the bottleneck problem (of the fixed-size output vector), allowing the model to process long-distance dependencies more easily. The name is because it "emulates searching through a source sentence during decoding a translation".[4]

The relative performances were compared between global (that of RNN search) and local (sliding window) attention model architectures for machine translation, finding that mixed attention had higher quality than global attention, while local attention reduced translation time.[27]

Parallelizing attention

Seq2seq models with attention (including self-attention) still suffered from the same issue with recurrent networks, which is that they are hard to parallelize, which prevented them from being accelerated on GPUs. In 2016, decomposable attention applied a self-attention mechanism to feedforward networks, which are easy to parallelize, and achieved SOTA result in textual entailment with an order of magnitude fewer parameters than LSTMs.[30] One of its authors, Jakob Uszkoreit, suspected that attention without recurrence would be sufficient for language translation, thus the title "attention is all you need".[31] That hypothesis was against conventional wisdom at the time, and even his father Hans Uszkoreit, a well-known computational linguist, was skeptical.[31] In the same year, self-attention (called intra-attention orintra-sentence attention) was proposed for LSTMs.[32]

In 2017, the original (100M-sized) encoder–decoder transformer model was proposed in the "Attention is all you need" paper. At the time, the focus of the research was on improving seq2seq for machine translation, by removing its recurrence to process all tokens in parallel, but preserving its dot-product attention mechanism to keep its text processing performance.[1] This led to the introduction of a multi-head attention model that was easier to parallelize due to the use of independent heads and the lack of recurrence. Its parallelizability was an important factor to its widespread use in large neural networks.[33]

AI boom era

Already in spring 2017, even before the "Attention is all you need" preprint was published, one of the co-authors applied the "decoder-only" variation of the architecture to generate fictitious Wikipedia articles.[34] Transformer architecture is now used alongside many generative models that contribute to the ongoing AI boom.

In language modelling, ELMo (2018) was a bi-directional LSTM that produces contextualized word embeddings, improving upon the line of research from bag of words and word2vec. It was followed by BERT (2018), an encoder-only transformer model.[35] In 2019 October, Google started using BERT to process search queries.[36] In 2020, Google Translate replaced the previous RNN-encoder–RNN-decoder model by a transformer-encoder–RNN-decoder model.[37]

Since 2020, transformers have been applied in modalities beyond text, including the vision transformer,[41] speech recognition,[42] robotics,[6] and multimodal.[43] The vision transformer, in turn, stimulated new developments in convolutional neural networks.[44] Image and video generators like DALL-E (2021), Stable Diffusion 3 (2024),[45] and Sora (2024), use transformers to analyse input data (like text prompts) by breaking it down into "tokens" and then calculating the relevance between each token using self-attention, which helps the model understand the context and relationships within the data.

Training

Methods for stabilizing training

The plain transformer architecture had difficulty in converging. In the original paper,[1] the authors recommended using learning rate warmup. That is, the learning rate should linearly scale up from 0 to maximal value for the first part of the training (usually recommended to be 2% of the total number of training steps), before decaying again.

A 2020 paper found that using layer normalizationbefore (instead of after) multihead attention and feedforward layers stabilizes training, not requiring learning rate warmup.[46]

Pretrain-finetune

Transformers typically are first pretrained by self-supervised learning on a large generic dataset, followed by supervisedfine-tuning on a small task-specific dataset. The pretrain dataset is typically an unlabeled large corpus, such as The Pile. Tasks for pretraining and fine-tuning commonly include:

judging the pragmatic acceptability of natural language. For example, the following sentence might be judged "not acceptable",[48] because even though it is syntactically well-formed, it is improbable in ordinary human usage: The course is jumping well.

Note that while each of these tasks is trivial or obvious for human native speakers of the language (or languages), they have typically proved challenging for previous generations of machine learning architecture.

Tasks

In general, there are 3 classes of language modelling tasks: "masked",[49] "autoregressive",[50] and "prefixLM".[51] These classes are independent of a specific modeling architecture such as transformer, but they are often discussed in the context of transformer.

In a masked task,[49] one or more of the tokens is masked out, and the model would produce a probability distribution predicting what the masked-out tokens are based on the context. The loss function for the task is typically sum of log-perplexities for the masked-out tokens: Loss=−∑t∈masked tokensln⁡(probability of t conditional on its context){\displaystyle {\text{Loss}}=-\sum _{t\in {\text{masked tokens}}}\ln({\text{probability of }}t{\text{ conditional on its context}})}and the model is trained to minimize this loss function. The BERT series of models are trained for masked token prediction and another task.

In an autoregressive task,[50] the entire sequence is masked at first, and the model produces a probability distribution for the first token. Then the first token is revealed and the model predicts the second token, and so on. The loss function for the task is still typically the same. The GPT series of models are trained by autoregressive tasks.

In a prefixLM task,[51] the sequence is divided into two parts. The first part is presented as context, and the model predicts the first token of the second part. Then that would be revealed, and the model predicts the second token, and so on. The loss function for the task is still typically the same. The T5 series of models are trained by prefixLM tasks.

Note that "masked" as in "masked language modelling" is not "masked" as in "masked attention", and "prefixLM" as in
"prefix language modeling" is not "prefixLM" as in " prefix language model".

Architecture

Embedding layer, which converts tokens and positions of the tokens into vector representations.

Transformer layers, which carry out repeated transformations on the vector representations, extracting more and more linguistic information. These consist of alternating attention and feedforward layers. There are two major types of transformer layers: encoder layers and decoder layers, with further variants.

Un-embedding layer, which converts the final vector representations back to a probability distribution over the tokens.

The following description follows exactly the transformer as described in the original paper. There are variants, described in the following section.

By convention, we write all vectors as row vectors. For example, pushing a vector through a linear layer means multiplying it by a weight matrix on the right, as xW{\displaystyle xW}.

Tokenization

As the transformer architecture natively consists of operations over numbers (matrix multiplications, dot products, activation functions) rather than over text, there must first be a mapping from any input text to some numerical representation. This happens in three steps.

First, the input text is treated by a preprocessor, which performs both textual transformations and splits the text into coarse-grained segments called pretokens. The latter is referred to as pretokenization. Second, each pretoken is segmented further into tokens by a tokenizer that expects to only see pretokens output by its preprocessor. Each token it produces is a string of one or more characters belonging to a finite set of strings called the vocabularyV{\displaystyle V}. Third, because the vocabulary is finite and known beforehand, each token can be assigned an integer identifier, and this mapping is applied to the sequence of tokens to represent any input text as a numerical sequence. Since this mapping is bijective, the output side can produce a sequence of integer identifiers which can then be turned back into tokens. After undoing some of the preprocessing, the result is again legible text.

Training a tokenizer (sometimes referred to as vocabularization) means finding a suitable vocabulary V{\displaystyle V}, but also learning how to use it, since any given string s{\displaystyle s} of length |s|{\displaystyle |s|} has 2|s|−1{\displaystyle 2^{|s|-1}} hypothetical segmentations, some of which containing segments that are not in the vocabulary. The most important hyperparameter during vocabularization is the vocabulary size|V|{\displaystyle |V|}: when it is small, the learned vocabulary generally consists of characters and smaller strings, and words will be segmented into many tokens. At larger sizes, it becomes affordable to dedicate tokens to full words, although depending on the preprocessor and tokenizer, it is not necessarily the case that large vocabularies will always use the largest token(s) available to segment a word.

Because tokens are not always full words, they may also be referred to as subwords and tokenization algorithms may be referred to as subword tokenizers. This is also to differentiate these systems from traditional terminology used in older information retrieval and natural language processing systems, where "tokenization" was used to denote what is today called "pretokenization" (very crudely: splitting into words). In tokenizers that produce tokens that are not part of the vocabulary, a special token that does belong to the vocabulary is used as a generic stand-in, written as "[UNK]" for "unknown". In principle, any string could be hidden by such an [UNK]. Indeed, in information retrieval, pretokenizers were themselves used as tokenizers (and also called "tokenizers") with a word-level vocabulary that contained an [UNK].

Commonly used subword tokenization algorithms are byte pair encoding (BPE) and the unigram language model (ULM), which each include a vocabularization algorithm and a dedicated segmentation algorithm. There also exist several segmentation algorithms that require no learning and can be applied given a vocabulary (produced by BPE or ULM, for example), like greedily recognising tokens in a pretoken by moving through it left-to-right. Well-known software implementations of subword tokenizers are Hugging Face's tokenizers Python package implemented in Rust, and the sentencepiece Python package implemented in C++. The latter package is named as such because one of its configuration options allows disabling the built-in pretokenizer, hence effectively making entire sentences a pretoken and thus having the tokenizer see entire sentences, rather than individual words.

Embedding

Each integer token identifier is converted into an embedding vector via a lookup table. Equivalently stated, it multiplies a one-hot representation of the token identifier by an embedding matrix M{\displaystyle M}. For example, if the input token's identifier is 3{\displaystyle 3}, then the one-hot representation is [0,0,0,1,0,0,…]{\displaystyle [0,0,0,1,0,0,\dots ]}, and its embedding vector isEmbed(3)=[0,0,0,1,0,0,…]M{\displaystyle \mathrm {Embed} (3)=[0,0,0,1,0,0,\dots ]M}The token embedding vectors are added to their respective positional encoding vectors (see below), producing the sequence of input vectors.

The dimension of an embedding vector is called hidden size or embedding size and written as demb{\displaystyle d_{\text{emb}}}.[35] This size is written as dmodel{\displaystyle d_{\text{model}}} in the original transformer paper.[1]

Un-embedding

An un-embedding layer is almost the reverse of an embedding layer. Whereas an embedding layer converts a token identifier into a vector, an un-embedding layer converts a vector into a probability distribution over tokens.

The un-embedding layer is a linear-softmax layer:UnEmbed(x)=softmax(xW+b){\displaystyle \mathrm {UnEmbed} (x)=\mathrm {softmax} (xW+b)}The matrix has shape (demb,|V|){\displaystyle (d_{\text{emb}},|V|)}. Some architectures use the transpose of the embedding matrix M{\displaystyle M} as the un-embedding matrix W{\displaystyle W} in order to avoid needing double the amount of embedding-related parameters and to avoid divergence during training. This practice is called weight tying.[52]

Positional encoding

A diagram of a sinusoidal positional encoding with parameters N=10000,d=100{\displaystyle N=10000,d=100}

A positional encoding is a fixed-size vector representation of the relative positions of tokens within a sequence: it provides the transformer model with information about where the words are in the input sequence. This induces a bias towards the order of the input sequence, so that, for example, the input sequence "man bites dog" is processed differently from "dog bites man".

The positional encoding is defined as a function of type f:R→Rd{\displaystyle f:\mathbb {R} \to \mathbb {R} ^{d}}, where d{\displaystyle d} is a positive even integer. The full positional encoding defined in the original paper[1] is:(f(t)2k,f(t)2k+1)=(sin⁡(θ),cos⁡(θ))∀k∈{0,1,…,d/2−1}{\displaystyle (f(t)_{2k},f(t)_{2k+1})=(\sin(\theta ),\cos(\theta ))\quad \forall k\in \{0,1,\ldots ,d/2-1\}}where θ=trk,r=N2/d{\displaystyle \theta ={\frac {t}{r^{k}}},r=N^{2/d}}.

Here, N{\displaystyle N} is a free parameter that should be significantly larger than the biggest k{\displaystyle k} that would be input into the positional encoding function. The original paper uses N=10000{\displaystyle N=10000}.

The function is in a simpler form when written as a complex function of type f:R→Cd/2{\displaystyle f:\mathbb {R} \to \mathbb {C} ^{d/2}}f(t)=(eit/rk)k=0,1,…,d2−1{\displaystyle f(t)=\left(e^{it/r^{k}}\right)_{k=0,1,\ldots ,{\frac {d}{2}}-1}}where r=N2/d{\displaystyle r=N^{2/d}}.

The main reason for using this positional encoding function is that using it, shifts are linear transformations:f(t+Δt)=diag(f(Δt))f(t){\displaystyle f(t+\Delta t)=\mathrm {diag} (f(\Delta t))f(t)}where Δt∈R{\displaystyle \Delta t\in \mathbb {R} } is the distance one wishes to shift. This allows the transformer to take any encoded position, and find the encoding of the position n-steps-ahead or n-steps-behind, by a matrix multiplication.

By taking a linear sum, any convolution can also be implemented as linear transformations:∑jcjf(t+Δtj)=(∑jcjdiag(f(Δtj)))f(t){\displaystyle \sum _{j}c_{j}f(t+\Delta t_{j})=\left(\sum _{j}c_{j}\,\mathrm {diag} (f(\Delta t_{j}))\right)f(t)}for any constants cj{\displaystyle c_{j}}. This allows the transformer to take any encoded position and find a linear sum of the encoded locations of its neighbors. This sum of encoded positions, when fed into the attention mechanism, would create attention weights on its neighbors, much like what happens in a convolutional neural networklanguage model. In the author's words, "we hypothesized it would allow the model to easily learn to attend by relative position."

Encoder–decoder (overview)

One encoder–decoder blockA transformer is composed of stacked encoder layers and decoder layers.

Like earlier seq2seq models, the original transformer model used an encoder–decoder architecture. The encoder consists of encoding layers that process all the input tokens together one layer after another, while the decoder consists of decoding layers that iteratively process the encoder's output and the decoder's output tokens so far.

The purpose of each encoder layer is to create contextualized representations of the tokens, where each representation corresponds to a token that "mixes" information from other input tokens via self-attention mechanism. Each decoder layer contains two attention sublayers: (1) cross-attention for incorporating the output of encoder (contextualized input token representations), and (2) self-attention for "mixing" information among the input tokens to the decoder (i.e. the tokens generated so far during inference time).[53][54]

Both the encoder and decoder layers have a feed-forward neural network for additional processing of their outputs and contain residual connections and layer normalization steps.[54] These feed-forward layers contain most of the parameters in a transformer model.

Feedforward network

The feedforward network module. It is a two-layered network that maps demb{\displaystyle d_{\text{emb}}}-dimensional vectors into demb{\displaystyle d_{\text{emb}}}-dimensional vectors.

The feedforward network (FFN) modules in a transformer are 2-layered multilayer perceptrons:FFN(x)=ϕ(xW(1)+b(1))W(2)+b(2){\displaystyle \mathrm {FFN} (x)=\phi (xW^{(1)}+b^{(1)})W^{(2)}+b^{(2)}}where W(1){\displaystyle W^{(1)}} and W(2){\displaystyle W^{(2)}} are weight matrices and b(1){\displaystyle b^{(1)}} and b(2){\displaystyle b^{(2)}} are bias vectors, and ϕ{\displaystyle \phi } is its activation function. The original transformer used ReLU activation.

The number of neurons in the middle layer is called intermediate size (GPT),[55]filter size (BERT),[35] or feedforward size (BERT).[35] It is typically larger than the embedding size. For example, in both GPT-2 series and BERT series, the intermediate size of a model is 4 times its embedding size: dffn=4demb{\displaystyle d_{\text{ffn}}=4d_{\text{emb}}}.

Scaled dot-product attention

Attention head

The attention mechanism used in the transformer architecture are scaled dot-productattention units. For each unit, the transformer model learns three weight matrices: the query weights WQ{\displaystyle W^{Q}}, the key weights WK{\displaystyle W^{K}}, and the value weights WV{\displaystyle W^{V}}.

The module takes three sequences, a query sequence, a key sequence, and a value sequence. The query sequence is a sequence of length ℓseq, query{\displaystyle \ell _{\text{seq, query}}}, and each entry is a vector of dimension demb, query{\displaystyle d_{\text{emb, query}}}. Similarly for the key and value sequences.

For each vector xi,query{\displaystyle x_{i,{\text{query}}}} in the query sequence, it is multiplied by a matrix WQ{\displaystyle W^{Q}} to produce a query vector qi=xi,queryWQ{\displaystyle q_{i}=x_{i,{\text{query}}}W^{Q}}. The matrix of all query vectors is the query matrix:Q=XqueryWQ{\displaystyle Q=X_{\text{query}}W^{Q}}Similarly, we construct the key matrix K=XkeyWK{\displaystyle K=X_{\text{key}}W^{K}} and the value matrix V=XvalueWV{\displaystyle V=X_{\text{value}}W^{V}}.

It is usually the case that all WQ,WK,WV{\displaystyle W^{Q},W^{K},W^{V}} are square matrices, meaning demb, query=dquery{\displaystyle d_{\text{emb, query}}=d_{\text{query}}}, etc.

Attention weights are calculated using the query and key vectors: the attention weight aij{\displaystyle a_{ij}} from token i{\displaystyle i} to token j{\displaystyle j} is the dot product between qi{\displaystyle q_{i}} and kj{\displaystyle k_{j}}. The attention weights are divided by the square root of the dimension of the key vectors, dk{\displaystyle {\sqrt {d_{k}}}}, which stabilizes gradients during training, and passed through a softmax which normalizes the weights. The fact that WQ{\displaystyle W^{Q}} and WK{\displaystyle W^{K}} are different matrices allows attention to be non-symmetric: if token i{\displaystyle i} attends to token j{\displaystyle j} (i.e. qi⋅kj{\displaystyle q_{i}\cdot k_{j}} is large), this does not necessarily mean that token j{\displaystyle j} will attend to token i{\displaystyle i} (i.e. qj⋅ki{\displaystyle q_{j}\cdot k_{i}} could be small). The output of the attention unit for token i{\displaystyle i} is the weighted sum of the value vectors of all tokens, weighted by aij{\displaystyle a_{ij}}, the attention from token i{\displaystyle i} to each token.

The attention calculation for all tokens can be expressed as one large matrix calculation using the softmax function, which is useful for training due to computational matrix operation optimizations that quickly compute matrix operations. The matrices Q{\displaystyle Q}, K{\displaystyle K} and V{\displaystyle V} are defined as the matrices where the i{\displaystyle i}th rows are vectors qi{\displaystyle q_{i}}, ki{\displaystyle k_{i}}, and vi{\displaystyle v_{i}} respectively. Then we can represent the attention asAttention(Q,K,V)=softmax(QKTdk)V{\displaystyle {\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\end{aligned}}}

where the softmax is applied over each of the rows of the matrix.

The number of dimensions in a query vector is query sizedquery{\displaystyle d_{\text{query}}} and similarly for the key sizedkey{\displaystyle d_{\text{key}}} and value sizedvalue{\displaystyle d_{\text{value}}}. The output dimension of an attention head is its head dimensiondhead{\displaystyle d_{\text{head}}}. The attention mechanism requires the following three equalities to hold:ℓseq, key=ℓseq, value,dquery=dkey,dvalue=dhead{\displaystyle \ell _{\text{seq, key}}=\ell _{\text{seq, value}},\;d_{\text{query}}=d_{\text{key}},\;d_{\text{value}}=d_{\text{head}}}but is otherwise unconstrained.

If the attention head is used in a self-attention fashion, then Xquery=Xkey=Xvalue{\displaystyle X_{\text{query}}=X_{\text{key}}=X_{\text{value}}}. If the attention head is used in a cross-attention fashion, then usually Xquery≠Xkey=Xvalue{\displaystyle X_{\text{query}}\neq X_{\text{key}}=X_{\text{value}}}. It is theoretically possible for all three to be different, but that is rarely the case in practice.

Multihead attention

One set of (WQ,WK,WV){\displaystyle \left(W^{Q},W^{K},W^{V}\right)} matrices is called an attention head, and each layer in a transformer model has multiple attention heads. While each attention head attends to the tokens that are relevant to each token, multiple attention heads allow the model to do this for different definitions of "relevance". Specifically, the query and key projection matrices, WQ{\displaystyle W^{Q}} and WK{\displaystyle W^{K}} , which are involved in the attention score computation, defines the "relevance". Meanwhile, the value projection matrixWV{\displaystyle W^{V}}, in combination with the part of the output projection matrix WO{\displaystyle W^{O}}, determines how the attended tokens influence what information is passed to subsequent layers and ultimately the output logits. In addition, the scope of attention, or the range of token relationships captured by each attention head, can expand as tokens pass through successive layers. This allows the model to capture more complex and long-range dependencies in deeper layers. Many transformer attention heads encode relevance relations that are meaningful to humans. For example, some attention heads can attend mostly to the next word, while others mainly attend from verbs to their direct objects.[56] The computations for each attention head can be performed in parallel, which allows for fast processing. The outputs for the attention layer are concatenated to pass into the feedforward neural network layers.

Concretely, let the multiple attention heads be indexed by i{\displaystyle i}, then we haveMultiheadAttention(Q,K,V)=Concati∈[nheads](Attention(XWiQ,XWiK,XWiV))WO{\displaystyle {\text{MultiheadAttention}}(Q,K,V)={\text{Concat}}_{i\in [n_{\text{heads}}]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}} where the matrix X{\displaystyle X} is the concatenation of word embeddings, and the matrices WiQ,WiK,WiV{\displaystyle W_{i}^{Q},W_{i}^{K},W_{i}^{V}} are "projection matrices" owned by individual attention head i{\displaystyle i}, and WO{\displaystyle W^{O}} is a final projection matrix owned by the whole multihead attention head.

It is theoretically possible for each attention head to have a different head dimension dhead{\displaystyle d_{\text{head}}}, but that is rarely the case in practice.

As an example, in the smallest GPT-2 model, there are only self-attention mechanisms. It has the following dimensions:demb=768,nhead=12,dhead=64{\displaystyle d_{\text{emb}}=768,n_{\text{head}}=12,d_{\text{head}}=64}Since 12×64=768{\displaystyle 12\times 64=768}, its output projection matrix WO∈R(12×64)×768{\displaystyle W^{O}\in \mathbb {R} ^{(12\times 64)\times 768}} is a square matrix.

Masked attention

The transformer architecture is constructed to calculate output tokens iteratively. Assuming t=0{\displaystyle t=0} refers to the calculation of the first output token i=0{\displaystyle i=0}, for step t>0{\displaystyle t>0}, the output token i=0{\displaystyle i=0} shall remain constant. This ensures properties of the model similar to autoregressive models.[1] Therefore, at every time step t{\displaystyle t}, the calculation for all outputs i{\displaystyle i} should not have access to tokens at position j{\displaystyle j} for j>=i{\displaystyle j>=i} (as it naturally is the case for time step t=i{\displaystyle t=i}, when tokens j>t{\displaystyle j>t} are not yet calculated). This behavior may be accomplished before the softmax stage by adding a mask matrix M{\displaystyle M} that is −∞{\displaystyle -\infty } at entries where the attention link must be cut, and 0{\displaystyle 0} at other places:MaskedAttention(Q,K,V)=softmax(M+QKTdk)V{\displaystyle {\begin{aligned}{\text{MaskedAttention}}(Q,K,V)={\text{softmax}}\left(M+{\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\end{aligned}}} The following matrix is commonly used in decoder self-attention modules, called "causal masking":Mcausal=[0−∞−∞…−∞00−∞…−∞000…−∞⋮⋮⋮⋱⋮000…0]{\displaystyle M_{\text{causal}}={\begin{bmatrix}0&-\infty &-\infty &\dots &-\infty \\0&0&-\infty &\dots &-\infty \\0&0&0&\dots &-\infty \\\vdots &\vdots &\vdots &\ddots &\vdots \\0&0&0&\dots &0\end{bmatrix}}}

In words, it means that each token can pay attention to itself, and every token before it, but not any after it. A non-masked attention module can be thought of as a masked attention module where the mask has all entries zero. As an example of an uncommon use of mask matrix, the XLNet considers all masks of the form PMcausalP−1{\displaystyle PM_{\text{causal}}P^{-1}}, where P{\displaystyle P} is a random permutation matrix.[57]

Encoder

An encoder consists of an embedding layer, followed by multiple encoder layers.

Each encoder layer consists of two major components: a self-attention mechanism and a feed-forward layer. It takes an input as a sequence of input vectors, applies the self-attention mechanism, to produce an intermediate sequence of vectors, then applies the feed-forward layer for each vector individually. Schematically, we have:given input vectors h0,h1,…combine them into a matrix H=[h0h1⋮]EncoderLayer(H)=[FFN(MultiheadAttention(H,H,H)0)FFN(MultiheadAttention(H,H,H)1)⋮]{\displaystyle {\begin{aligned}{\text{given input vectors }}&h_{0},h_{1},\dots \\{\text{combine them into a matrix }}H&={\begin{bmatrix}h_{0}\\h_{1}\\\vdots \end{bmatrix}}\\{\text{EncoderLayer}}(H)&={\begin{bmatrix}{\text{FFN}}({\text{MultiheadAttention}}(H,H,H)_{0})\\{\text{FFN}}({\text{MultiheadAttention}}(H,H,H)_{1})\\\vdots \end{bmatrix}}\\\end{aligned}}}

where FFN{\displaystyle {\text{FFN}}} stands for "feed-forward network". We can more succinctly write it asEncoderLayer(H)=FFN(MultiheadAttention(H,H,H)){\displaystyle {\text{EncoderLayer}}(H)={\text{FFN}}({\text{MultiheadAttention}}(H,H,H))}with the implicit convention that the FFN{\displaystyle {\text{FFN}}} is applied to each row of the matrix individually.

The encoder layers are stacked. The first encoder layer takes the sequence of input vectors from the embedding layer, producing a sequence of vectors. This sequence of vectors is processed by the second encoder, and so on. The output from the final encoder layer is then used by the decoder.

As the encoder processes the entire input all at once, every token can attend to every other token (all-to-all attention), so there is no need for causal masking.

Decoder

A decoder consists of an embedding layer, followed by multiple decoder layers, followed by an un-embedding layer.

Each decoder consists of three major components: a causally masked self-attention mechanism, a cross-attention mechanism, and a feed-forward neural network. The decoder functions in a similar fashion to the encoder, but an additional attention mechanism is inserted which instead draws relevant information from the encodings generated by the encoders. This mechanism can also be called the encoder–decoder attention.[1][54]

Like the first encoder, the first decoder takes positional information and embeddings of the output sequence as its input, rather than encodings. The transformer must not use the current or future output to predict an output, so the output sequence must be partially masked to prevent this reverse information flow.[1] This allows for autoregressive text generation. For decoding, all-to-all attention is inappropriate, because a token cannot attend to tokens not yet generated. Thus, the self-attention module in the decoder is causally masked.

In contrast, the cross-attention mechanism attends to the output vectors of the encoder, which is computed before the decoder starts decoding. Consequently, there is no need for masking in the cross-attention mechanism.

Schematically, we have:H′=MaskedMultiheadAttention(H,H,H)DecoderLayer(H)=FFN(MultiheadAttention(H′,HE,HE)){\displaystyle {\begin{aligned}H'&={\text{MaskedMultiheadAttention}}(H,H,H)\\{\text{DecoderLayer}}(H)&={\text{FFN}}({\text{MultiheadAttention}}(H',H^{E},H^{E}))\end{aligned}}}where HE{\displaystyle H^{E}} is the matrix with rows being the output vectors from the encoder.

The last decoder is followed by a final un-embedding layer to produce the output probabilities over the vocabulary. Then, one of the tokens is sampled according to the probability, and the decoder can be run again to produce the next token, etc., autoregressively generating output text.

Adapted architectures

Many large language models, since they do not need to predict a whole new sequence from an input sequence, only use the encoder or decoder of the original transformer architecture. Early GPT models are decoder-only models trained to predict the next token in a sequence.[58]BERT, another language model, only makes use of an encoder, and is trained to predict a randomly masked token in a sequence.[35]

Full transformer architecture

Sublayers

(a) One encoder layer and one decoder layer. (b) Two encoder layers and two decoder layers. The sublayers are labelled as well.

Each encoder layer contains 2 sublayers: the self-attention and the feedforward network. Each decoder layer contains 3 sublayers: the causally masked self-attention, the cross-attention, and the feedforward network.

Transformer encoder with norm-first and norm-lastTransformer decoder with norm-first and norm-lastBlock diagram for the full transformer architectureSchematic object hierarchy for the full transformer architecture, in object-oriented programming style

The final points of detail are the residual connections and layer normalization, (denoted as "LayerNorm", or "LN" in the following), which while conceptually unnecessary, are necessary for numerical stability and convergence.

The residual connection, which is introduced to avoid vanishing gradient issues and stabilize the training process, can be expressed as follows: y = F(x) + x. The expression indicates that an output y is the sum of the transformation of input x (F(x)) and the input itself (x). Adding the input x can preserve the input information and avoid issues when the gradient of F(x) is close to zero.

Similarly to how the feedforward network modules are applied individually to each vector, the LayerNorm is also applied individually to each vector.

There are two common conventions in use: the post-LN and the pre-LN convention. In the post-LN convention, the output of each sublayer is LayerNorm(x+Sublayer(x)){\displaystyle \mathrm {LayerNorm} (x+\mathrm {Sublayer} (x))}where Sublayer(x){\displaystyle \mathrm {Sublayer} (x)} is the function implemented by the sublayer itself.

In the pre-LN convention, the output of each sublayer isx+Sublayer(LayerNorm(x)){\displaystyle x+\mathrm {Sublayer} (\mathrm {LayerNorm} (x))}The original 2017 transformer used the post-LN convention. It was difficult to train and required careful hyperparameter tuning and a "warm-up" in learning rate, where it starts small and gradually increases. The pre-LN convention, proposed several times in 2018,[59] was found to be easier to train, requiring no warm-up, leading to faster convergence.[46]

Terminology

The transformer architecture, being modular, allows variations. Several common variations are described here.[61]

An "encoder-only" transformer applies the encoder to map an input text into a sequence of vectors that represent the input text. This is usually used for text embedding and representation learning for downstream applications. BERT is encoder-only. They are less often used currently, as they were found to be not significantly better than training an encoder–decoder transformer, then taking just the encoder.[51]

A "decoder-only" transformer is not literally decoder-only, since without an encoder, the cross-attention mechanism has nothing to attend to. Thus, the decoder layers in a decoder-only transformer is composed of just two sublayers: the causally masked self-attention, and the feedforward network. This is usually used for text generation and instruction following. The models in the GPT series and Chinchilla series are decoder-only.

An "encoder–decoder" transformer is generally the same as the original transformer, with 2 sublayers per encoder layer and 3 sublayers per decoder layer, etc. They might have minor architectural improvements, such as alternative activation functions, changing the location of normalization, etc. This is also usually used for text generation and instruction following. The models in the T5 series are encoder–decoder.[61]

A "prefixLM" (prefix language model) is a decoder-only architecture, but with prefix masking, which is different from causal masking. Specifically, it has mask of the form[61]: Figure 3 MprefixLM=[0−∞0Mcausal]{\displaystyle M_{\text{prefixLM}}={\begin{bmatrix}\mathbf {0} &-\infty \\\mathbf {0} &M_{\text{causal}}\end{bmatrix}}}where the first columns correspond to the "prefix", and the subsequent columns correspond to the autoregressively generated text based on the prefix. They resemble encoder–decoder models, but has less "sparsity". Such models are rarely used, though they are cited as theoretical possibilities and benchmarked comparisons.[51]

There are also mixed seq2seq models. For example, in 2020, Google Translate replaced the previous RNN-encoder–RNN-decoder model with a transformer-encoder–RNN-decoder model, as transformer-based decoders did not appear to significantly increase quality unlike the encoder, while the RNN decoder was much faster.[37]

Alternative normalizations

The normalization used in the transformer can be different from LayerNorm. One example is RMSNorm[64] which is used in the Llama series. Other examples include CapsuleNorm[65] ScaleNorm,[66] or FixNorm.[66]

Alternative positional encodings

Transformers may use other positional encoding methods than sinusoidal.[67]

The original transformer paper reported using a learned positional encoding,[68] but finding it not superior to the sinusoidal one.[1] Later,[69] found that causal masking itself provides enough signal to a transformer decoder that it can learn to implicitly perform absolute positional encoding without the positional encoding module.

The benefit of RoPE is that the dot-product between two vectors depends on their relative location only:RoPE(x,m)TRoPE(y,n)=RoPE(x,m+k)TRoPE(y,n+k){\displaystyle {\text{RoPE}}{\big (}x,m{\big )}^{T}{\text{RoPE}}{\big (}y,n{\big )}={\text{RoPE}}{\big (}x,m+k{\big )}^{T}{\text{RoPE}}{\big (}y,n+k{\big )}}
for any integer k{\displaystyle k}.

ALiBi

ALiBi (Attention with Linear Biases)[71] is not a replacement for the positional encoder on the original transformer. Instead, it is an additional positional encoder that is directly plugged into the attention mechanism. Specifically, the ALiBi attention mechanism isAttention(Q,K,V)=softmax(QKTdk+sB)V{\displaystyle {\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}+sB\right)V\end{aligned}}}Here, s{\displaystyle s} is a real number ("scalar"), and B{\displaystyle B} is the linear bias matrix defined byB=(0123⋯−1012⋯−2−101⋯−3−2−10⋯⋮⋮⋮⋮⋱){\displaystyle B={\begin{pmatrix}0&1&2&3&\cdots \\-1&0&1&2&\cdots \\-2&-1&0&1&\cdots \\-3&-2&-1&0&\cdots \\\vdots &\vdots &\vdots &\vdots &\ddots \\\end{pmatrix}}}in other words, Bi,j=j−i{\displaystyle B_{i,j}=j-i}. The idea being that the linear bias matrix is a softened mask. Just as 0{\displaystyle 0} represent full attention paid, and −∞{\displaystyle -\infty } represents no attention paid, the linear bias matrix increases attention paid in one direction and decreases attention paid in the other direction.

ALiBi allows pretraining on short context windows, then fine-tuning on longer context windows. Since it is directly plugged into the attention mechanism, it can be combined with any positional encoder that is plugged into the "bottom" of the entire network (which is where the sinusoidal encoder on the original transformer, as well as RoPE and many others, are located).

Relative Position Encodings

Relative Position Encodings[72] is similar to ALiBi, but more generic:Attention(Q,K,V)=softmax(QKTdk+B)V{\displaystyle {\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}+B\right)V\end{aligned}}}where B{\displaystyle B} is a Toeplitz matrix, that is, Bi,j=Bi′,j′{\displaystyle B_{i,j}=B_{i',j'}} whenever i−j=i′−j′{\displaystyle i-j=i'-j'}. This is contrasted with the original sinusoidal positional encoding, which is an "absolute positional encoding".[73]

Efficient implementation

The transformer model has been implemented in standard deep learning frameworks such as TensorFlow and PyTorch. Transformers is a library produced by Hugging Face that supplies transformer-based architectures and pretrained models.[11]

KV caching

When an autoregressive transformer is used for inference, such as generating text, the query vector is different at each step, but the already-computed key and value vectors are always the same. The KV caching method saves the computed key and value vectors at each attention block, so that they are not recomputed at each new token. PagedAttention applies memory paging to KV caching.[74][75][76]

If a transformer is used with a baked-in prompt, such as ["You are a customer support agent..."], then the key and value vectors can be computed for the prompt, and saved on disk. The saving in compute is significant when the model is used for many short real-time interactions, such as in online chatbots.

FlashAttention

FlashAttention[77] is an algorithm that implements the transformer attention mechanism efficiently on a GPU. It is a communication-avoiding algorithm that performs matrix multiplications in blocks, such that each block fits within the cache of a GPU, and by careful management of the blocks it minimizes data copying between GPU caches (as data movement is slow). See the page on softmax for details.

An improved version, FlashAttention-2,[78][79][80] was developed to cater to the rising demand for language models capable of handling longer context lengths. It offers enhancements in work partitioning and parallelism, enabling it to achieve up to 230 TFLOPs/s on A100 GPUs (FP16/BF16), a 2x speed increase over the original FlashAttention.

Key advancements in FlashAttention-2 include the reduction of non-matmul FLOPs, improved parallelism over the sequence length dimension, better work partitioning between GPU warps, and added support for head dimensions up to 256 and multi-query attention (MQA) and grouped-query attention (GQA).[81]

Benchmarks revealed FlashAttention-2 to be up to 2x faster than FlashAttention and up to 9x faster than a standard attention implementation in PyTorch. Future developments include optimization for new hardware like H100 GPUs and new data types like FP8.

MultiheadAttention(Q,K,V)=Concati∈[nheads](Attention(XWiQ,XWiK,XWiV))WO{\displaystyle {\text{MultiheadAttention}}(Q,K,V)={\text{Concat}}_{i\in [n_{\text{heads}}]}\left({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V})\right)W^{O}}with Multi-Query Attention, there is just one WK,WV{\displaystyle W^{K},W^{V}}, thus:

This has a neutral effect on model quality and training speed, but increases inference speed.

More generally, grouped-query attention (GQA) partitions attention heads into groups, each of which shares the key-value pair. MQA is GQA with one group, while standard Multihead Attention is GQA with the maximal number of groups.[84]

Multihead Latent Attention (MLA) is a low-rank approximation to standard MHA. Specifically, each hidden vector, before entering the attention mechanism, is first projected to two low-dimensional spaces ("latent space"), one for query and one for key-value (KV vector). This design minimizes the KV cache, as only the low-dimensional KV vector needs to be cached.[85]

Speculative decoding

Speculative decoding[86][87] is a method to accelerate token decoding. Similarly to speculative execution in CPUs, future tokens are computed quickly, then verified. If the quickly computed tokens are incorrect, they are discarded and computed slowly.

The key factor in speculative decoding is that a transformer decoder can verify faster than it can decode, in the following sense.

Suppose we have two transformer models like GPT-3 and GPT-3-small, both with a context window size of 512. To generate an entire context window autoregressively with greedy decoding with GPT-3, it must be run for 512 times, each time generating a token x1,x2,...,x512{\displaystyle x_{1},x_{2},...,x_{512}}, taking time 512TGPT-3{\displaystyle 512T_{\text{GPT-3}}}. However, if we had some educated guess for the values of these tokens, we could verify all of them in parallel, in one run of the model, by checking that each xt{\displaystyle x_{t}} is indeed the token with the largest log-likelihood in the t{\displaystyle t}-th output.

In speculative decoding, a smaller model or some other simple heuristic is used to generate a few speculative tokens that are subsequently verified by the larger model. For example, suppose we use GPT-3-small to generate four speculative tokens: x~1,x~2,x~3,x~4{\displaystyle {\tilde {x}}_{1},{\tilde {x}}_{2},{\tilde {x}}_{3},{\tilde {x}}_{4}}. This only takes 4TGPT-3-small{\displaystyle 4T_{\text{GPT-3-small}}}. These tokens are then run through the larger GPT-3 in one go. Suppose that x~1{\displaystyle {\tilde {x}}_{1}} and x~2{\displaystyle {\tilde {x}}_{2}} are verified by GPT-3 as what it would have picked, then those are kept, but x~3{\displaystyle {\tilde {x}}_{3}} is not, so x~3,x~4{\displaystyle {\tilde {x}}_{3},{\tilde {x}}_{4}} are discarded, and GPT-3 is run on those. This would take 4TGPT-3-small+3TGPT-3{\displaystyle 4T_{\text{GPT-3-small}}+3T_{\text{GPT-3}}}, which might be shorter than 4TGPT-3{\displaystyle 4T_{\text{GPT-3}}}.

For non-greedy decoding, similar ideas apply, except the speculative tokens are accepted or rejected stochastically, in a way that guarantees the final output distribution is the same as if speculative decoding was not used.[86][88]

Multi-token prediction

In Multi-Token Prediction, a single forward pass creates a final embedding vector, which then is un-embedded into a token probability. However, that vector can then be further processed by another transformer block to predict the next token, and so on for arbitrarily many steps into the future. This trades off accuracy for speed, since each new token costs just one more transformer block, rather than the entire stack.[89][90]

Sub-quadratic transformers

Training transformer-based architectures can be expensive, especially for long inputs.[91] Many methods have been developed to attempt to address the issue. In the image domain, Swin transformer is an efficient architecture that performs attention inside shifting windows.[92] In the audio domain, SepTr decouples the attention in time and frequency domains.[93]Long Range Arena (2020)[94] is a standard benchmark for comparing the behavior of transformer architectures over long inputs.

Ordinary transformers require a memory size that is quadratic in the size of the context window. Attention-free transformers[99] reduce this to a linear dependence while still retaining the advantages of a transformer by linking the key to the value.

This approximation can be computed in linear time, as we can compute the matrix φ(ki)viT{\displaystyle \varphi (k_{i})v_{i}^{T}} first, then multiply it with the query. In essence, we have managed to obtain a more precise version of Attention(Q,K,V)=softmax(QKTdk)V≈Q(KTV/dk){\displaystyle {\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\approx Q(K^{T}V/{\sqrt {d_{k}}})}Performer (2022)[101] uses the same Random Feature Attention, but w1,...,wD{\displaystyle w_{1},...,w_{D}} are first independently sampled from the normal distribution N(0,σ2I){\displaystyle N(0,\sigma ^{2}I)}, then they are Gram-Schmidt processed.

Multimodality

Transformers can also be used/adapted for modalities (input or output) beyond just text, usually by finding a way to "tokenize" the modality.

Multimodal models can either be trained from scratch, or by finetuning. A 2022 study found that transformers pretrained only on natural language can be finetuned on only 0.03% of parameters and become competitive with LSTMs on a variety of logical and visual tasks, demonstrating transfer learning.[102] The LLaVA was a vision-language model composed of a language model (Vicuna-13B)[103] and a vision model (ViT-L/14), connected by a linear layer. Only the linear layer is finetuned.[104]

Vision transformers[41] adapt the transformer to computer vision by breaking down input images as a series of patches, turning them into vectors, and treating them like embedding vector of tokens in a standard transformer.

Conformer[42] and later Whisper[105] follow the same pattern for speech recognition, first turning the speech signal into a spectrogram, which is then treated like an image, i.e. broken down into a series of patches, turned into vectors and treated like embedding vector of tokens in a standard transformer.

For image generation, notable architectures are DALL-E 1 (2021), Parti (2022),[108] Phenaki (2023),[109] and Muse (2023).[110] Unlike later models, DALL-E is not a diffusion model. Instead, it uses a decoder-only transformer that autoregressively generates a text, followed by the token representation of an image, which is then converted by a variational autoencoder to an image.[111] Parti is an encoder–decoder transformer, where the encoder processes a text prompt, and the decoder generates a token representation of an image.[112] Muse is an encoder-only transformer that is trained to predict masked image tokens from unmasked image tokens. During generation, all input tokens are masked, and the highest-confidence predictions are included for the next iteration, until all tokens are predicted.[110] Phenaki is a text-to-video model. It is a bidirectional masked transformer conditioned on pre-computed text tokens. The generated tokens are then decoded to a video.[109]