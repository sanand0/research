Jump to content

Main menu

Main menu

move to sidebar hide

Navigation

  * [Main page](/wiki/Main_Page "Visit the main page \[z\]")
  * [Contents](/wiki/Wikipedia:Contents "Guides to browsing Wikipedia")
  * [Current events](/wiki/Portal:Current_events "Articles related to current events")
  * [Random article](/wiki/Special:Random "Visit a randomly selected article \[x\]")
  * [About Wikipedia](/wiki/Wikipedia:About "Learn about Wikipedia and how it works")
  * [Contact us](//en.wikipedia.org/wiki/Wikipedia:Contact_us "How to contact Wikipedia")

Contribute

  * [Help](/wiki/Help:Contents "Guidance on how to use and edit Wikipedia")
  * [Learn to edit](/wiki/Help:Introduction "Learn how to edit Wikipedia")
  * [Community portal](/wiki/Wikipedia:Community_portal "The hub for editors")
  * [Recent changes](/wiki/Special:RecentChanges "A list of recent changes to Wikipedia \[r\]")
  * [Upload file](/wiki/Wikipedia:File_upload_wizard "Add images or other media for use on Wikipedia")
  * [Special pages](/wiki/Special:SpecialPages)

[ ![](/static/images/icons/wikipedia.png)
![Wikipedia](/static/images/mobile/copyright/wikipedia-wordmark-en.svg) ![The
Free Encyclopedia](/static/images/mobile/copyright/wikipedia-tagline-en.svg)
](/wiki/Main_Page)

[ Search ](/wiki/Special:Search "Search Wikipedia \[f\]")

Search

Appearance

  * [Donate](https://donate.wikimedia.org/?wmf_source=donate&wmf_medium=sidebar&wmf_campaign=en.wikipedia.org&uselang=en)
  * [Create account](/w/index.php?title=Special:CreateAccount&returnto=Transformer+%28deep+learning%29 "You are encouraged to create an account and log in; however, it is not mandatory")
  * [Log in](/w/index.php?title=Special:UserLogin&returnto=Transformer+%28deep+learning%29 "You're encouraged to log in; however, it's not mandatory. \[o\]")

Personal tools

  * [Donate](https://donate.wikimedia.org/?wmf_source=donate&wmf_medium=sidebar&wmf_campaign=en.wikipedia.org&uselang=en)
  * [ Create account](/w/index.php?title=Special:CreateAccount&returnto=Transformer+%28deep+learning%29 "You are encouraged to create an account and log in; however, it is not mandatory")
  * [ Log in](/w/index.php?title=Special:UserLogin&returnto=Transformer+%28deep+learning%29 "You're encouraged to log in; however, it's not mandatory. \[o\]")

## Contents

move to sidebar hide

  * (Top)
  * 1 History Toggle History subsection
    * 1.1 Predecessors
    * 1.2 Attention with seq2seq
    * 1.3 Parallelizing attention
    * 1.4 AI boom era
  * 2 Training Toggle Training subsection
    * 2.1 Methods for stabilizing training
    * 2.2 Pretrain-finetune
    * 2.3 Tasks
  * 3 Architecture Toggle Architecture subsection
    * 3.1 Tokenization
    * 3.2 Embedding
    * 3.3 Un-embedding
    * 3.4 Positional encoding
    * 3.5 Encoder–decoder (overview)
    * 3.6 Feedforward network
    * 3.7 Scaled dot-product attention
      * 3.7.1 Attention head
      * 3.7.2 Multihead attention
      * 3.7.3 Masked attention
    * 3.8 Encoder
    * 3.9 Decoder
    * 3.10 Adapted architectures
  * 4 Full transformer architecture Toggle Full transformer architecture subsection
    * 4.1 Sublayers
    * 4.2 Pseudocode
    * 4.3 Terminology
  * 5 Subsequent work Toggle Subsequent work subsection
    * 5.1 Alternative activation functions
    * 5.2 Alternative normalizations
    * 5.3 Alternative positional encodings
      * 5.3.1 RoPE
      * 5.3.2 ALiBi
      * 5.3.3 Relative Position Encodings
    * 5.4 Efficient implementation
      * 5.4.1 KV caching
      * 5.4.2 FlashAttention
      * 5.4.3 Multi-Query Attention
      * 5.4.4 Speculative decoding
    * 5.5 Sub-quadratic transformers
      * 5.5.1 Alternative attention graphs
      * 5.5.2 Random Feature Attention
    * 5.6 Multimodality
  * 6 Applications
  * 7 See also
  * 8 Notes
  * 9 References
  * 10 Further reading

Toggle the table of contents

# Transformer (deep learning)

30 languages

  * [العربية](https://ar.wikipedia.org/wiki/%D9%85%D8%AD%D9%88%D9%84_\(%D8%AA%D8%B9%D9%84%D9%85_%D8%A7%D9%84%D8%A2%D9%84%D8%A9\) "محول \(تعلم الآلة\) – Arabic")
  * [Català](https://ca.wikipedia.org/wiki/Transformador_\(model_d%27aprenentatge_autom%C3%A0tic\) "Transformador \(model d'aprenentatge automàtic\) – Catalan")
  * [Čeština](https://cs.wikipedia.org/wiki/Transform%C3%A1tor_\(model_strojov%C3%A9ho_u%C4%8Den%C3%AD\) "Transformátor \(model strojového učení\) – Czech")
  * [Deutsch](https://de.wikipedia.org/wiki/Transformer_\(Maschinelles_Lernen\) "Transformer \(Maschinelles Lernen\) – German")
  * [Eesti](https://et.wikipedia.org/wiki/Transformer_\(masin%C3%B5pe\) "Transformer \(masinõpe\) – Estonian")
  * [Español](https://es.wikipedia.org/wiki/Transformador_\(modelo_de_aprendizaje_autom%C3%A1tico\) "Transformador \(modelo de aprendizaje automático\) – Spanish")
  * [Euskara](https://eu.wikipedia.org/wiki/Transformer_\(ikasketa_automatikoko_eredua\) "Transformer \(ikasketa automatikoko eredua\) – Basque")
  * [فارسی](https://fa.wikipedia.org/wiki/%D8%AA%D8%B1%D9%86%D8%B3%D9%81%D9%88%D8%B1%D9%85%D8%B1_\(%DB%8C%D8%A7%D8%AF%DA%AF%DB%8C%D8%B1%DB%8C_%D8%B9%D9%85%DB%8C%D9%82\) "ترنسفورمر \(یادگیری عمیق\) – Persian")
  * [Français](https://fr.wikipedia.org/wiki/Transformeur "Transformeur – French")
  * [Gaeilge](https://ga.wikipedia.org/wiki/Trasfhoirmeoir_\(ailtireacht_domhainfhoghlama\) "Trasfhoirmeoir \(ailtireacht domhainfhoghlama\) – Irish")
  * [Galego](https://gl.wikipedia.org/wiki/Transformador_\(modelo_de_aprendizaxe_autom%C3%A1tica\) "Transformador \(modelo de aprendizaxe automática\) – Galician")
  * [한국어](https://ko.wikipedia.org/wiki/%ED%8A%B8%EB%9E%9C%EC%8A%A4%ED%8F%AC%EB%A8%B8_\(%EA%B8%B0%EA%B3%84_%ED%95%99%EC%8A%B5\) "트랜스포머 \(기계 학습\) – Korean")
  * [Հայերեն](https://hy.wikipedia.org/wiki/%D5%8F%D6%80%D5%A1%D5%B6%D5%BD%D6%86%D5%B8%D6%80%D5%B4%D5%A5%D6%80_\(%D5%AD%D5%B8%D6%80_%D5%B8%D6%82%D5%BD%D5%B8%D6%82%D6%81%D5%B8%D6%82%D5%B4\) "Տրանսֆորմեր \(խոր ուսուցում\) – Armenian")
  * [Italiano](https://it.wikipedia.org/wiki/Trasformatore_\(informatica\) "Trasformatore \(informatica\) – Italian")
  * [עברית](https://he.wikipedia.org/wiki/%D7%98%D7%A8%D7%A0%D7%A1%D7%A4%D7%95%D7%A8%D7%9E%D7%A8_\(%D7%9C%D7%9E%D7%99%D7%93%D7%AA_%D7%9E%D7%9B%D7%95%D7%A0%D7%94\) "טרנספורמר \(למידת מכונה\) – Hebrew")
  * [日本語](https://ja.wikipedia.org/wiki/Transformer_\(%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92%E3%83%A2%E3%83%87%E3%83%AB\) "Transformer \(機械学習モデル\) – Japanese")
  * [Norsk nynorsk](https://nn.wikipedia.org/wiki/Transformator_i_djupl%C3%A6ring "Transformator i djuplæring – Norwegian Nynorsk")
  * [Polski](https://pl.wikipedia.org/wiki/Transformer_\(sztuczna_inteligencja\) "Transformer \(sztuczna inteligencja\) – Polish")
  * [Qaraqalpaqsha](https://kaa.wikipedia.org/wiki/Transformator_\(tere%C5%84_oq%C4%B1t%C4%B1w_arxitekturas%C4%B1\) "Transformator \(tereń oqıtıw arxitekturası\) – Kara-Kalpak")
  * [Русский](https://ru.wikipedia.org/wiki/%D0%A2%D1%80%D0%B0%D0%BD%D1%81%D1%84%D0%BE%D1%80%D0%BC%D0%B5%D1%80_\(%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C_%D0%BC%D0%B0%D1%88%D0%B8%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE_%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D1%8F\) "Трансформер \(модель машинного обучения\) – Russian")
  * [Simple English](https://simple.wikipedia.org/wiki/Transformer_\(machine_learning_model\) "Transformer \(machine learning model\) – Simple English")
  * [کوردی](https://ckb.wikipedia.org/wiki/%D8%AA%D8%B1%D8%A7%D9%86%D8%B3%D9%81%DB%86%D8%B1%D9%85%DB%95%D8%B1_\(%D9%85%DB%86%D8%AF%DB%8E%D9%84%DB%8C_%D9%81%DB%8E%D8%B1%D8%A8%D9%88%D9%88%D9%86%DB%8C_%D8%A6%D8%A7%D9%85%DB%8E%D8%B1\) "ترانسفۆرمەر \(مۆدێلی فێربوونی ئامێر\) – Central Kurdish")
  * [Српски / srpski](https://sr.wikipedia.org/wiki/Transformator_\(model_ma%C5%A1inskog_u%C4%8Denja\) "Transformator \(model mašinskog učenja\) – Serbian")
  * [Svenska](https://sv.wikipedia.org/wiki/Transformator_\(maskininl%C3%A4rningsmodell\) "Transformator \(maskininlärningsmodell\) – Swedish")
  * [ไทย](https://th.wikipedia.org/wiki/%E0%B8%97%E0%B8%A3%E0%B8%B2%E0%B8%99%E0%B8%AA%E0%B9%8C%E0%B8%9F%E0%B8%AD%E0%B8%A3%E0%B9%8C%E0%B9%80%E0%B8%A1%E0%B8%AD%E0%B8%A3%E0%B9%8C "ทรานส์ฟอร์เมอร์ – Thai")
  * [Türkçe](https://tr.wikipedia.org/wiki/Transformer_\(derin_%C3%B6%C4%9Frenme_mimarisi\) "Transformer \(derin öğrenme mimarisi\) – Turkish")
  * [Українська](https://uk.wikipedia.org/wiki/%D0%A2%D1%80%D0%B0%D0%BD%D1%81%D1%84%D0%BE%D1%80%D0%BC%D0%B5%D1%80_\(%D0%B0%D1%80%D1%85%D1%96%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0_%D0%B3%D0%BB%D0%B8%D0%B1%D0%BE%D0%BA%D0%BE%D0%B3%D0%BE_%D0%BD%D0%B0%D0%B2%D1%87%D0%B0%D0%BD%D0%BD%D1%8F\) "Трансформер \(архітектура глибокого навчання\) – Ukrainian")
  * [Tiếng Việt](https://vi.wikipedia.org/wiki/Transformer_\(m%C3%B4_h%C3%ACnh_h%E1%BB%8Dc_m%C3%A1y\) "Transformer \(mô hình học máy\) – Vietnamese")
  * [粵語](https://zh-yue.wikipedia.org/wiki/Transformer_\(%E6%A9%9F%E6%A2%B0%E5%AD%B8%E7%BF%92%E6%A8%A1%E5%9E%8B\) "Transformer \(機械學習模型\) – Cantonese")
  * [中文](https://zh.wikipedia.org/wiki/Transformer%E6%9E%B6%E6%9E%84 "Transformer架构 – Chinese")

[Edit
links](https://www.wikidata.org/wiki/Special:EntityPage/Q85810444#sitelinks-
wikipedia "Edit interlanguage links")

  * [Article](/wiki/Transformer_\(deep_learning\) "View the content page \[c\]")
  * [Talk](/wiki/Talk:Transformer_\(deep_learning\) "Discuss improvements to the content page \[t\]")

English

  * [Read](/wiki/Transformer_\(deep_learning\))
  * [Edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit "Edit this page \[e\]")
  * [View history](/w/index.php?title=Transformer_\(deep_learning\)&action=history "Past revisions of this page \[h\]")

Tools

Tools

move to sidebar hide

Actions

  * [Read](/wiki/Transformer_\(deep_learning\))
  * [Edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit "Edit this page \[e\]")
  * [View history](/w/index.php?title=Transformer_\(deep_learning\)&action=history)

General

  * [What links here](/wiki/Special:WhatLinksHere/Transformer_\(deep_learning\) "List of all English Wikipedia pages containing links to this page \[j\]")
  * [Related changes](/wiki/Special:RecentChangesLinked/Transformer_\(deep_learning\) "Recent changes in pages linked from this page \[k\]")
  * [Upload file](//en.wikipedia.org/wiki/Wikipedia:File_Upload_Wizard "Upload files \[u\]")
  * [Permanent link](/w/index.php?title=Transformer_\(deep_learning\)&oldid=1321325230 "Permanent link to this revision of this page")
  * [Page information](/w/index.php?title=Transformer_\(deep_learning\)&action=info "More information about this page")
  * [Cite this page](/w/index.php?title=Special:CiteThisPage&page=Transformer_%28deep_learning%29&id=1321325230&wpFormIdentifier=titleform "Information on how to cite this page")
  * [Get shortened URL](/w/index.php?title=Special:UrlShortener&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FTransformer_%28deep_learning%29)
  * [Download QR code](/w/index.php?title=Special:QrCode&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FTransformer_%28deep_learning%29)

Print/export

  * [Download as PDF](/w/index.php?title=Special:DownloadAsPdf&page=Transformer_%28deep_learning%29&action=show-download-screen "Download this page as a PDF file")
  * [Printable version](/w/index.php?title=Transformer_\(deep_learning\)&printable=yes "Printable version of this page \[p\]")

In other projects

  * [Wikidata item](https://www.wikidata.org/wiki/Special:EntityPage/Q85810444 "Structured data on this page hosted by Wikidata \[g\]")

Appearance

move to sidebar hide

From Wikipedia, the free encyclopedia

(Redirected from [Transformer (deep learning
architecture)](/w/index.php?title=Transformer_\(deep_learning_architecture\)&redirect=no
"Transformer \(deep learning architecture\)"))

Algorithm for modelling sequential data

Part of a series on  
---  
[Machine learning](/wiki/Machine_learning "Machine learning")  
and [data mining](/wiki/Data_mining "Data mining")  
Paradigms

  * [Supervised learning](/wiki/Supervised_learning "Supervised learning")
  * [Unsupervised learning](/wiki/Unsupervised_learning "Unsupervised learning")
  * [Semi-supervised learning](/wiki/Semi-supervised_learning "Semi-supervised learning")
  * [Self-supervised learning](/wiki/Self-supervised_learning "Self-supervised learning")
  * [Reinforcement learning](/wiki/Reinforcement_learning "Reinforcement learning")
  * [Meta-learning](/wiki/Meta-learning_\(computer_science\) "Meta-learning \(computer science\)")
  * [Online learning](/wiki/Online_machine_learning "Online machine learning")
  * [Batch learning](/wiki/Batch_learning "Batch learning")
  * [Curriculum learning](/wiki/Curriculum_learning "Curriculum learning")
  * [Rule-based learning](/wiki/Rule-based_machine_learning "Rule-based machine learning")
  * [Neuro-symbolic AI](/wiki/Neuro-symbolic_AI "Neuro-symbolic AI")
  * [Neuromorphic engineering](/wiki/Neuromorphic_engineering "Neuromorphic engineering")
  * [Quantum machine learning](/wiki/Quantum_machine_learning "Quantum machine learning")

  
Problems

  * [Classification](/wiki/Statistical_classification "Statistical classification")
  * [Generative modeling](/wiki/Generative_model "Generative model")
  * [Regression](/wiki/Regression_analysis "Regression analysis")
  * [Clustering](/wiki/Cluster_analysis "Cluster analysis")
  * [Dimensionality reduction](/wiki/Dimensionality_reduction "Dimensionality reduction")
  * [Density estimation](/wiki/Density_estimation "Density estimation")
  * [Anomaly detection](/wiki/Anomaly_detection "Anomaly detection")
  * [Data cleaning](/wiki/Data_cleaning "Data cleaning")
  * [AutoML](/wiki/Automated_machine_learning "Automated machine learning")
  * [Association rules](/wiki/Association_rule_learning "Association rule learning")
  * [Semantic analysis](/wiki/Semantic_analysis_\(machine_learning\) "Semantic analysis \(machine learning\)")
  * [Structured prediction](/wiki/Structured_prediction "Structured prediction")
  * [Feature engineering](/wiki/Feature_engineering "Feature engineering")
  * [Feature learning](/wiki/Feature_learning "Feature learning")
  * [Learning to rank](/wiki/Learning_to_rank "Learning to rank")
  * [Grammar induction](/wiki/Grammar_induction "Grammar induction")
  * [Ontology learning](/wiki/Ontology_learning "Ontology learning")
  * [Multimodal learning](/wiki/Multimodal_learning "Multimodal learning")

  
[Supervised learning](/wiki/Supervised_learning "Supervised learning")  
(**[classification](/wiki/Statistical_classification "Statistical
classification")** • **[regression](/wiki/Regression_analysis "Regression
analysis")**)

  * [Apprenticeship learning](/wiki/Apprenticeship_learning "Apprenticeship learning")
  * [Decision trees](/wiki/Decision_tree_learning "Decision tree learning")
  * [Ensembles](/wiki/Ensemble_learning "Ensemble learning")
    * [Bagging](/wiki/Bootstrap_aggregating "Bootstrap aggregating")
    * [Boosting](/wiki/Boosting_\(machine_learning\) "Boosting \(machine learning\)")
    * [Random forest](/wiki/Random_forest "Random forest")
  * [_k_ -NN](/wiki/K-nearest_neighbors_algorithm "K-nearest neighbors algorithm")
  * [Linear regression](/wiki/Linear_regression "Linear regression")
  * [Naive Bayes](/wiki/Naive_Bayes_classifier "Naive Bayes classifier")
  * [Artificial neural networks](/wiki/Artificial_neural_network "Artificial neural network")
  * [Logistic regression](/wiki/Logistic_regression "Logistic regression")
  * [Perceptron](/wiki/Perceptron "Perceptron")
  * [Relevance vector machine (RVM)](/wiki/Relevance_vector_machine "Relevance vector machine")
  * [Support vector machine (SVM)](/wiki/Support_vector_machine "Support vector machine")

  
[Clustering](/wiki/Cluster_analysis "Cluster analysis")

  * [BIRCH](/wiki/BIRCH "BIRCH")
  * [CURE](/wiki/CURE_algorithm "CURE algorithm")
  * [Hierarchical](/wiki/Hierarchical_clustering "Hierarchical clustering")
  * [_k_ -means](/wiki/K-means_clustering "K-means clustering")
  * [Fuzzy](/wiki/Fuzzy_clustering "Fuzzy clustering")
  * [Expectation–maximization (EM)](/wiki/Expectation%E2%80%93maximization_algorithm "Expectation–maximization algorithm")
  *   
[DBSCAN](/wiki/DBSCAN "DBSCAN")

  * [OPTICS](/wiki/OPTICS_algorithm "OPTICS algorithm")
  * [Mean shift](/wiki/Mean_shift "Mean shift")

  
[Dimensionality reduction](/wiki/Dimensionality_reduction "Dimensionality
reduction")

  * [Factor analysis](/wiki/Factor_analysis "Factor analysis")
  * [CCA](/wiki/Canonical_correlation "Canonical correlation")
  * [ICA](/wiki/Independent_component_analysis "Independent component analysis")
  * [LDA](/wiki/Linear_discriminant_analysis "Linear discriminant analysis")
  * [NMF](/wiki/Non-negative_matrix_factorization "Non-negative matrix factorization")
  * [PCA](/wiki/Principal_component_analysis "Principal component analysis")
  * [PGD](/wiki/Proper_generalized_decomposition "Proper generalized decomposition")
  * [t-SNE](/wiki/T-distributed_stochastic_neighbor_embedding "T-distributed stochastic neighbor embedding")
  * [SDL](/wiki/Sparse_dictionary_learning "Sparse dictionary learning")

  
[Structured prediction](/wiki/Structured_prediction "Structured prediction")

  * [Graphical models](/wiki/Graphical_model "Graphical model")
    * [Bayes net](/wiki/Bayesian_network "Bayesian network")
    * [Conditional random field](/wiki/Conditional_random_field "Conditional random field")
    * [Hidden Markov](/wiki/Hidden_Markov_model "Hidden Markov model")

  
[Anomaly detection](/wiki/Anomaly_detection "Anomaly detection")

  * [RANSAC](/wiki/Random_sample_consensus "Random sample consensus")
  * [_k_ -NN](/wiki/K-nearest_neighbors_algorithm "K-nearest neighbors algorithm")
  * [Local outlier factor](/wiki/Local_outlier_factor "Local outlier factor")
  * [Isolation forest](/wiki/Isolation_forest "Isolation forest")

  
[Neural networks](/wiki/Neural_network_\(machine_learning\) "Neural network
\(machine learning\)")

  * [Autoencoder](/wiki/Autoencoder "Autoencoder")
  * [Deep learning](/wiki/Deep_learning "Deep learning")
  * [Feedforward neural network](/wiki/Feedforward_neural_network "Feedforward neural network")
  * [Recurrent neural network](/wiki/Recurrent_neural_network "Recurrent neural network")
    * [LSTM](/wiki/Long_short-term_memory "Long short-term memory")
    * [GRU](/wiki/Gated_recurrent_unit "Gated recurrent unit")
    * [ESN](/wiki/Echo_state_network "Echo state network")
    * [reservoir computing](/wiki/Reservoir_computing "Reservoir computing")
  * [Boltzmann machine](/wiki/Boltzmann_machine "Boltzmann machine")
    * [Restricted](/wiki/Restricted_Boltzmann_machine "Restricted Boltzmann machine")
  * [GAN](/wiki/Generative_adversarial_network "Generative adversarial network")
  * [Diffusion model](/wiki/Diffusion_model "Diffusion model")
  * [SOM](/wiki/Self-organizing_map "Self-organizing map")
  * [Convolutional neural network](/wiki/Convolutional_neural_network "Convolutional neural network")
    * [U-Net](/wiki/U-Net "U-Net")
    * [LeNet](/wiki/LeNet "LeNet")
    * [AlexNet](/wiki/AlexNet "AlexNet")
    * [DeepDream](/wiki/DeepDream "DeepDream")
  * [Neural field](/wiki/Neural_field "Neural field")
    * [Neural radiance field](/wiki/Neural_radiance_field "Neural radiance field")
    * [Physics-informed neural networks](/wiki/Physics-informed_neural_networks "Physics-informed neural networks")
  * [Transformer](/wiki/Transformer_\(deep_learning_architecture\) "Transformer \(deep learning architecture\)")
    * [Vision](/wiki/Vision_transformer "Vision transformer")
  * [Mamba](/wiki/Mamba_\(deep_learning_architecture\) "Mamba \(deep learning architecture\)")
  * [Spiking neural network](/wiki/Spiking_neural_network "Spiking neural network")
  * [Memtransistor](/wiki/Memtransistor "Memtransistor")
  * [Electrochemical RAM](/wiki/Electrochemical_RAM "Electrochemical RAM") (ECRAM)

  
[Reinforcement learning](/wiki/Reinforcement_learning "Reinforcement
learning")

  * [Q-learning](/wiki/Q-learning "Q-learning")
  * [Policy gradient](/wiki/Policy_gradient_method "Policy gradient method")
  * [SARSA](/wiki/State%E2%80%93action%E2%80%93reward%E2%80%93state%E2%80%93action "State–action–reward–state–action")
  * [Temporal difference (TD)](/wiki/Temporal_difference_learning "Temporal difference learning")
  * [Multi-agent](/wiki/Multi-agent_reinforcement_learning "Multi-agent reinforcement learning")
    * [Self-play](/wiki/Self-play_\(reinforcement_learning_technique\) "Self-play \(reinforcement learning technique\)")

  
Learning with humans

  * [Active learning](/wiki/Active_learning_\(machine_learning\) "Active learning \(machine learning\)")
  * [Crowdsourcing](/wiki/Crowdsourcing "Crowdsourcing")
  * [Human-in-the-loop](/wiki/Human-in-the-loop "Human-in-the-loop")
  * [Mechanistic interpretability](/wiki/Mechanistic_interpretability "Mechanistic interpretability")
  * [RLHF](/wiki/Reinforcement_learning_from_human_feedback "Reinforcement learning from human feedback")

  
Model diagnostics

  * [Coefficient of determination](/wiki/Coefficient_of_determination "Coefficient of determination")
  * [Confusion matrix](/wiki/Confusion_matrix "Confusion matrix")
  * [Learning curve](/wiki/Learning_curve_\(machine_learning\) "Learning curve \(machine learning\)")
  * [ROC curve](/wiki/Receiver_operating_characteristic "Receiver operating characteristic")

  
Mathematical foundations

  * [Kernel machines](/wiki/Kernel_machines "Kernel machines")
  * [Bias–variance tradeoff](/wiki/Bias%E2%80%93variance_tradeoff "Bias–variance tradeoff")
  * [Computational learning theory](/wiki/Computational_learning_theory "Computational learning theory")
  * [Empirical risk minimization](/wiki/Empirical_risk_minimization "Empirical risk minimization")
  * [Occam learning](/wiki/Occam_learning "Occam learning")
  * [PAC learning](/wiki/Probably_approximately_correct_learning "Probably approximately correct learning")
  * [Statistical learning](/wiki/Statistical_learning_theory "Statistical learning theory")
  * [VC theory](/wiki/Vapnik%E2%80%93Chervonenkis_theory "Vapnik–Chervonenkis theory")
  * [Topological deep learning](/wiki/Topological_deep_learning "Topological deep learning")

  
Journals and conferences

  * [AAAI](/wiki/AAAI_Conference_on_Artificial_Intelligence "AAAI Conference on Artificial Intelligence")
  * [ECML PKDD](/wiki/ECML_PKDD "ECML PKDD")
  * [NeurIPS](/wiki/Conference_on_Neural_Information_Processing_Systems "Conference on Neural Information Processing Systems")
  * [ICML](/wiki/International_Conference_on_Machine_Learning "International Conference on Machine Learning")
  * [ICLR](/wiki/International_Conference_on_Learning_Representations "International Conference on Learning Representations")
  * [IJCAI](/wiki/International_Joint_Conference_on_Artificial_Intelligence "International Joint Conference on Artificial Intelligence")
  * [ML](/wiki/Machine_Learning_\(journal\) "Machine Learning \(journal\)")
  * [JMLR](/wiki/Journal_of_Machine_Learning_Research "Journal of Machine Learning Research")

  
Related articles

  * [Glossary of artificial intelligence](/wiki/Glossary_of_artificial_intelligence "Glossary of artificial intelligence")
  * [List of datasets for machine-learning research](/wiki/List_of_datasets_for_machine-learning_research "List of datasets for machine-learning research")
    * [List of datasets in computer vision and image processing](/wiki/List_of_datasets_in_computer_vision_and_image_processing "List of datasets in computer vision and image processing")
  * [Outline of machine learning](/wiki/Outline_of_machine_learning "Outline of machine learning")

  
  
  * [v](/wiki/Template:Machine_learning "Template:Machine learning")
  * [t](/wiki/Template_talk:Machine_learning "Template talk:Machine learning")
  * [e](/wiki/Special:EditPage/Template:Machine_learning "Special:EditPage/Template:Machine learning")

  
[![](//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/250px-
Transformer%2C_full_architecture.png)](/wiki/File:Transformer,_full_architecture.png)A
standard transformer architecture, showing on the left an encoder, and on the
right a decoder. Note: it uses the pre-LN convention, which is different from
the post-LN convention used in the original 2017 transformer.

In [deep learning](/wiki/Deep_learning "Deep learning"), the **transformer**
is a neural network architecture based on the multi-head
[attention](/wiki/Attention_\(machine_learning\) "Attention \(machine
learning\)") mechanism, in which text is converted to numerical
representations called [tokens](/wiki/Large_language_model#Tokenization "Large
language model"), and each token is converted into a vector via lookup from a
[word embedding](/wiki/Word_embedding "Word embedding") table.[1] At each
layer, each [token](/wiki/Tokenization_\(lexical_analysis\) "Tokenization
\(lexical analysis\)") is then
[contextualized](/wiki/Contextualization_\(computer_science\)
"Contextualization \(computer science\)") within the scope of the [context
window](/wiki/Context_window "Context window") with other (unmasked) tokens
via a parallel multi-head attention mechanism, allowing the signal for key
tokens to be amplified and less important tokens to be diminished.

Transformers have the advantage of having no recurrent units, therefore
requiring less training time than earlier [recurrent neural
architectures](/wiki/Recurrent_neural_network "Recurrent neural network")
(RNNs) such as [long short-term memory](/wiki/Long_short-term_memory "Long
short-term memory") (LSTM).[2] Later variations have been widely adopted for
training [large language models](/wiki/Large_language_model "Large language
model") (LLMs) on large (language)
[datasets](/wiki/Training,_validation,_and_test_data_sets "Training,
validation, and test data sets").[3]

The modern version of the transformer was proposed in the 2017 paper
"[Attention Is All You Need](/wiki/Attention_Is_All_You_Need "Attention Is All
You Need")" by researchers at [Google](/wiki/Google "Google").[1] The
predecessors of transformers were developed as an improvement over previous
architectures for [machine translation](/wiki/Machine_translation "Machine
translation"),[4][5] but have found many applications since. They are used in
large-scale [natural language processing](/wiki/Natural_language_processing
"Natural language processing"), [computer vision](/wiki/Computer_vision
"Computer vision") ([vision transformers](/wiki/Vision_transformer "Vision
transformer")), [reinforcement learning](/wiki/Reinforcement_learning
"Reinforcement learning"),[6][7] [audio](/wiki/Audio_signal_processing "Audio
signal processing"),[8] [multimodal learning](/wiki/Multimodal_learning
"Multimodal learning"), [robotics](/wiki/Robotics "Robotics"),[9] and even
playing [chess](/wiki/Computer_chess "Computer chess").[10] It has also led to
the development of [pre-trained systems](/wiki/Transfer_learning "Transfer
learning"), such as [generative pre-trained
transformers](/wiki/Generative_pre-trained_transformer "Generative pre-trained
transformer") (GPTs)[11] and [BERT](/wiki/BERT_\(language_model\) "BERT
\(language model\)")[12] (bidirectional encoder representations from
transformers).

## History

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=1
"Edit section: History")]

See also: [Timeline of machine learning](/wiki/Timeline_of_machine_learning
"Timeline of machine learning")

### Predecessors

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=2
"Edit section: Predecessors")]

For many years, sequence modelling and generation was done by using plain
[recurrent neural networks](/wiki/Recurrent_neural_network "Recurrent neural
network") (RNNs). A well-cited early example was the [Elman
network](/wiki/Elman_network "Elman network") (1990). In theory, the
information from one token can propagate arbitrarily far down the sequence,
but in practice the [vanishing-gradient problem](/wiki/Vanishing-
gradient_problem "Vanishing-gradient problem") leaves the model's state at the
end of a long sentence without precise, extractable information about
preceding tokens.

A key breakthrough was [LSTM](/wiki/Long_short-term_memory "Long short-term
memory") (1995),[note 1] an RNN which used various innovations to overcome the
vanishing gradient problem, allowing efficient learning of long-sequence
modelling. One key innovation was the use of an [attention
mechanism](/wiki/Attention_\(machine_learning\) "Attention \(machine
learning\)") which used neurons that multiply the outputs of other neurons,
so-called _multiplicative units_.[13] Neural networks using multiplicative
units were later called _sigma-pi networks_[14] or _[higher-order
networks](/w/index.php?title=Higher-order_neural_network&action=edit&redlink=1
"Higher-order neural network \(page does not exist\)")_.[15] LSTM became the
standard architecture for long sequence modelling until the 2017 publication
of transformers. However, LSTM still used sequential processing, like most
other RNNs.[note 2] Specifically, RNNs operate one token at a time from first
to last; they cannot operate in parallel over all tokens in a sequence.

Modern transformers overcome this problem, but unlike RNNs, they require
computation time that is [quadratic](/wiki/Quadratic_function "Quadratic
function") in the size of the context window. The linearly scaling [fast
weight](/w/index.php?title=Fast_weight&action=edit&redlink=1 "Fast weight
\(page does not exist\)") controller (1992) learns to compute a weight matrix
for further processing depending on the input.[16] One of its two networks has
"fast weights" or "dynamic links" (1981).[17][18][19] A slow neural network
learns by gradient descent to generate keys and values for computing the
weight changes of the fast neural network which computes answers to
queries.[16] This was later shown to be equivalent to the unnormalized linear
transformer.[20][21]

### Attention with seq2seq

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=3
"Edit section: Attention with seq2seq")]

Main article: [Seq2seq § History](/wiki/Seq2seq#History "Seq2seq")

The idea of encoder–decoder sequence transduction had been developed in the
early 2010s; commonly cited as the originators that produced seq2seq are two
concurrently published papers from 2014.[22][23]

A 380M-parameter model for machine translation uses two [long short-term
memories](/wiki/Long_short-term_memory "Long short-term memory") (LSTM).[23]
Its architecture consists of two parts. The _encoder_ is an LSTM that takes in
a sequence of tokens and turns it into a vector. The _decoder_ is another LSTM
that converts the vector into a sequence of tokens. Similarly, another
130M-parameter model used [gated recurrent units](/wiki/Gated_recurrent_unit
"Gated recurrent unit") (GRU) instead of LSTM.[22] Later research showed that
GRUs are neither better nor worse than LSTMs for seq2seq.[24][25]

These early seq2seq models had no attention mechanism, and the state vector is
accessible only after the _last_ word of the source text was processed.
Although in theory such a vector retains the information about the whole
original sentence, in practice the information is poorly preserved. This is
because the input is processed sequentially by one recurrent network into a
_fixed_ -size output vector, which is then processed by another recurrent
network into an output. If the input is long, then the output vector would not
be able to contain all relevant information, degrading the output. As
evidence, reversing the input sentence improved seq2seq translation.[26]

The _RNN search_ model introduced an attention mechanism to seq2seq for
machine translation to solve the bottleneck problem (of the _fixed-size_
output vector), allowing the model to process long-distance dependencies more
easily. The name is because it "emulates searching through a source sentence
during decoding a translation".[4]

The relative performances were compared between global (that of _RNN search_)
and local (sliding window) attention model architectures for machine
translation, finding that mixed attention had higher quality than global
attention, while local attention reduced translation time.[27]

In 2016, [Google Translate](/wiki/Google_Translate "Google Translate") was
revamped to [Google Neural Machine
Translation](/wiki/Google_Neural_Machine_Translation "Google Neural Machine
Translation"), which replaced the previous model based on [statistical machine
translation](/wiki/Statistical_machine_translation "Statistical machine
translation"). The new model was a seq2seq model where the encoder and the
decoder were both 8 layers of bidirectional LSTM.[28] It took nine months to
develop, and it outperformed the statistical approach, which took ten years to
develop.[29]

### Parallelizing attention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=4
"Edit section: Parallelizing attention")]

Main article: [Attention (machine learning) §
History](/wiki/Attention_\(machine_learning\)#History "Attention \(machine
learning\)")

Seq2seq models with attention (including self-attention) still suffered from
the same issue with recurrent networks, which is that they are hard to
[parallelize](/wiki/Parallel_computing "Parallel computing"), which prevented
them from being accelerated on GPUs. In 2016, _decomposable attention_ applied
a self-attention mechanism to [feedforward
networks](/wiki/Feedforward_neural_network "Feedforward neural network"),
which are easy to parallelize, and achieved [SOTA](/wiki/State_of_the_art
"State of the art") result in [textual entailment](/wiki/Textual_entailment
"Textual entailment") with an order of magnitude fewer parameters than
LSTMs.[30] One of its authors, Jakob Uszkoreit, suspected that attention
_without_ recurrence would be sufficient for language translation, thus the
title "attention is _all_ you need".[31] That hypothesis was against
conventional wisdom at the time, and even his father [Hans
Uszkoreit](/wiki/Hans_Uszkoreit "Hans Uszkoreit"), a well-known computational
linguist, was skeptical.[31] In the same year, self-attention (called _intra-
attention or_ _intra-sentence attention_) was proposed for LSTMs.[32]

In 2017, the original (100M-sized) encoder–decoder transformer model was
proposed in the "[Attention is all you need](/wiki/Attention_is_all_you_need
"Attention is all you need")" paper. At the time, the focus of the research
was on improving [seq2seq](/wiki/Seq2seq "Seq2seq") for [machine
translation](/wiki/Machine_translation "Machine translation"), by removing its
recurrence to process all tokens in parallel, but preserving its dot-product
attention mechanism to keep its text processing performance.[1] This led to
the introduction of a multi-head attention model that was easier to
parallelize due to the use of independent heads and the lack of recurrence.
Its parallelizability was an important factor to its widespread use in large
neural networks.[33]

### AI boom era

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=5
"Edit section: AI boom era")]

Already in spring 2017, even before the "Attention is all you need" preprint
was published, one of the co-authors applied the "decoder-only" variation of
the architecture to generate fictitious Wikipedia articles.[34] Transformer
architecture is now used alongside many [generative
models](/wiki/Generative_artificial_intelligence "Generative artificial
intelligence") that contribute to the ongoing [AI boom](/wiki/AI_boom "AI
boom").

In language modelling, [ELMo](/wiki/ELMo "ELMo") (2018) was a bi-directional
LSTM that produces contextualized [word embeddings](/wiki/Word_embedding "Word
embedding"), improving upon the line of research from [bag of
words](/wiki/Bag-of-words_model "Bag-of-words model") and
[word2vec](/wiki/Word2vec "Word2vec"). It was followed by
[BERT](/wiki/BERT_\(language_model\) "BERT \(language model\)") (2018), an
encoder-only transformer model.[35] In 2019 October, Google started using BERT
to process search queries.[36] In 2020, Google Translate replaced the previous
RNN-encoder–RNN-decoder model by a transformer-encoder–RNN-decoder model.[37]

Starting in 2018, the OpenAI [GPT series](/wiki/Generative_pre-
trained_transformer "Generative pre-trained transformer") of decoder-only
transformers became state of the art in [natural language
generation](/wiki/Natural_language_generation "Natural language generation").
In 2022, a chatbot based on GPT-3, [ChatGPT](/wiki/ChatGPT "ChatGPT"), became
unexpectedly[38] popular, triggering a boom around [large language
models](/wiki/Large_language_model "Large language model").[39][40]

Since 2020, transformers have been applied in modalities beyond text,
including the [vision transformer](/wiki/Vision_transformer "Vision
transformer"),[41] speech recognition,[42] robotics,[6] and
[multimodal](/wiki/Multimodal_learning "Multimodal learning").[43] The vision
transformer, in turn, stimulated new developments in [convolutional neural
networks](/wiki/Convolutional_neural_network "Convolutional neural
network").[44] Image and video generators like [DALL-E](/wiki/DALL-E "DALL-E")
(2021), [Stable Diffusion 3](/wiki/Stable_Diffusion "Stable Diffusion")
(2024),[45] and [Sora](/wiki/Sora_\(text-to-video_model\) "Sora \(text-to-
video model\)") (2024), use transformers to analyse input data (like text
prompts) by breaking it down into "tokens" and then calculating the relevance
between each token using self-attention, which helps the model understand the
context and relationships within the data.

## Training

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=6
"Edit section: Training")]

### Methods for stabilizing training

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=7
"Edit section: Methods for stabilizing training")]

The plain transformer architecture had difficulty in converging. In the
original paper,[1] the authors recommended using [learning
rate](/wiki/Learning_rate "Learning rate") warmup. That is, the learning rate
should linearly scale up from 0 to maximal value for the first part of the
training (usually recommended to be 2% of the total number of training steps),
before decaying again.

A 2020 paper found that using [layer normalization](/wiki/Layer_normalization
"Layer normalization") _before_ (instead of after) multihead attention and
feedforward layers stabilizes training, not requiring learning rate
warmup.[46]

### Pretrain-finetune

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=8
"Edit section: Pretrain-finetune")]

Transformers typically are first pretrained by [self-supervised
learning](/wiki/Self-supervised_learning "Self-supervised learning") on a
large generic dataset, followed by [supervised](/wiki/Supervised_learning
"Supervised learning") [fine-tuning](/wiki/Fine-tuning_\(deep_learning\)
"Fine-tuning \(deep learning\)") on a small task-specific dataset. The
pretrain dataset is typically an unlabeled large corpus, such as [The
Pile](/wiki/The_Pile_\(dataset\) "The Pile \(dataset\)"). Tasks for
pretraining and fine-tuning commonly include:

  * [language modeling](/wiki/Language_modeling "Language modeling")[12]
  * next-sentence prediction[12]
  * [question answering](/wiki/Question_answering "Question answering")[3]
  * [reading comprehension](/wiki/Natural-language_understanding "Natural-language understanding")
  * [sentiment analysis](/wiki/Sentiment_analysis "Sentiment analysis")[1]
  * [paraphrasing](/wiki/Text_Summaries "Text Summaries")[1]

The [T5 transformer](/wiki/T5_\(language_model\) "T5 \(language model\)")
report[47] documents a large number of [natural
language](/wiki/Natural_language "Natural language") pretraining tasks. Some
examples are:

  * restoring or repairing incomplete or corrupted text. For example, the input, _"Thank you ~~ me to your party ~~ week",_ might generate the output, _"Thank you**for inviting** me to your party **last** week"._
  * translation between natural languages ([machine translation](/wiki/Machine_translation "Machine translation"))
  * judging the pragmatic acceptability of natural language. For example, the following sentence might be judged "not acceptable",[48] because even though it is syntactically well-formed, it is improbable in ordinary human usage: _The course is jumping well._

Note that while each of these tasks is trivial or obvious for human native
speakers of the language (or languages), they have typically proved
challenging for previous generations of machine learning architecture.

### Tasks

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=9
"Edit section: Tasks")]

See also: [Large language model §
Evaluation](/wiki/Large_language_model#Evaluation "Large language model")

In general, there are 3 classes of language modelling tasks: "masked",[49]
"autoregressive",[50] and "prefixLM".[51] These classes are independent of a
specific modeling architecture such as transformer, but they are often
discussed in the context of transformer.

In a masked task,[49] one or more of the tokens is masked out, and the model
would produce a probability distribution predicting what the masked-out tokens
are based on the context. The [loss function](/wiki/Loss_function "Loss
function") for the task is typically sum of [log-
perplexities](/wiki/Perplexity "Perplexity") for the masked-out tokens:  Loss
= − ∑ t ∈ masked tokens ln ⁡ ( probability of t conditional on its context )
{\displaystyle {\text{Loss}}=-\sum _{t\in {\text{masked
tokens}}}\ln({\text{probability of }}t{\text{ conditional on its context}})}
![{\\displaystyle {\\text{Loss}}=-\\sum _{t\\in {\\text{masked
tokens}}}\\ln\({\\text{probability of }}t{\\text{ conditional on its
context}}\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/55f0855cde2d171c96b77251ce43de9ee3cfd4e8)and
the model is trained to minimize this loss function. The [BERT series of
models](/wiki/BERT_\(language_model\) "BERT \(language model\)") are trained
for masked token prediction and another task.

In an autoregressive task,[50] the entire sequence is masked at first, and the
model produces a probability distribution for the first token. Then the first
token is revealed and the model predicts the second token, and so on. The loss
function for the task is still typically the same. The [GPT series of
models](/wiki/Generative_pre-trained_transformer "Generative pre-trained
transformer") are trained by autoregressive tasks.

In a prefixLM task,[51] the sequence is divided into two parts. The first part
is presented as context, and the model predicts the first token of the second
part. Then that would be revealed, and the model predicts the second token,
and so on. The loss function for the task is still typically the same. The [T5
series of models](/wiki/T5_\(language_model\) "T5 \(language model\)") are
trained by prefixLM tasks.

Note that "masked" as in "masked language modelling" is not "masked" as in
"masked attention", and "prefixLM" as in "prefix language modeling" is not
"prefixLM" as in " prefix language model".

## Architecture

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=10
"Edit section: Architecture")]

All transformers have the same primary components:

  * Tokenizers, which convert text into tokens.
  * Embedding layer, which converts tokens and positions of the tokens into vector representations.
  * Transformer layers, which carry out repeated transformations on the vector representations, extracting more and more linguistic information. These consist of alternating attention and feedforward layers. There are two major types of transformer layers: encoder layers and decoder layers, with further variants.
  * Un-embedding layer, which converts the final vector representations back to a probability distribution over the tokens.

The following description follows exactly the transformer as described in the
original paper. There are variants, described in the following section.

By convention, we write all vectors as row vectors. For example, pushing a
vector through a linear layer means multiplying it by a weight matrix on the
right, as  x W {\displaystyle xW} ![{\\displaystyle
xW}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b366d97326adb9cbb74e22c5ee0966dd055cd2dc).

### Tokenization

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=11
"Edit section: Tokenization")]

As the transformer architecture natively consists of operations over numbers
(matrix multiplications, dot products, activation functions) rather than over
text, there must first be a mapping from any input text to some numerical
representation. This happens in three steps.

First, the input text is treated by a _preprocessor_ , which performs both
textual transformations and splits the text into coarse-grained segments
called _pretokens_. The latter is referred to as _pretokenization_. Second,
each pretoken is segmented further into _tokens_ by a _tokenizer_ that expects
to only see pretokens output by its preprocessor. Each token it produces is a
string of one or more characters belonging to a finite set of strings called
the _vocabulary_ V {\displaystyle V} ![{\\displaystyle
V}](https://wikimedia.org/api/rest_v1/media/math/render/svg/af0f6064540e84211d0ffe4dac72098adfa52845).
Third, because the vocabulary is finite and known beforehand, each token can
be assigned an integer identifier, and this mapping is applied to the sequence
of tokens to represent any input text as a numerical sequence. Since this
mapping is bijective, the output side can produce a sequence of integer
identifiers which can then be turned back into tokens. After undoing some of
the preprocessing, the result is again legible text.

Training a tokenizer (sometimes referred to as _vocabularization_) means finding a suitable vocabulary  V {\displaystyle V} ![{\\displaystyle V}](https://wikimedia.org/api/rest_v1/media/math/render/svg/af0f6064540e84211d0ffe4dac72098adfa52845), but also learning how to use it, since any given string  s {\displaystyle s} ![{\\displaystyle s}](https://wikimedia.org/api/rest_v1/media/math/render/svg/01d131dfd7673938b947072a13a9744fe997e632) of length  | s | {\displaystyle |s|} ![{\\displaystyle |s|}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0ae65dea0cc836140252292ee9adf2d8b5102055) has  2 | s | − 1 {\displaystyle 2^{|s|-1}} ![{\\displaystyle 2^{|s|-1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3d844850486603030caed10d1c3d330d604770b8) hypothetical segmentations, some of which containing segments that are not in the vocabulary. The most important hyperparameter during vocabularization is the _vocabulary size_ | V | {\displaystyle |V|} ![{\\displaystyle |V|}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9ddcffc28643ac01a14dd0fb32c3157859e365a7): when it is small, the learned vocabulary generally consists of characters and smaller strings, and words will be segmented into many tokens. At larger sizes, it becomes affordable to dedicate tokens to full words, although depending on the preprocessor and tokenizer, it is not necessarily the case that large vocabularies will always use the largest token(s) available to segment a word. 

Because tokens are not always full words, they may also be referred to as
_subwords_ and tokenization algorithms may be referred to as _subword
tokenizers_. This is also to differentiate these systems from [traditional
terminology](/wiki/Lexical_analysis "Lexical analysis") used in older
information retrieval and natural language processing systems, where
"tokenization" was used to denote what is today called "pretokenization" (very
crudely: splitting into words). In tokenizers that produce tokens that are
_not_ part of the vocabulary, a special token that does belong to the
vocabulary is used as a generic stand-in, written as "[UNK]" for "unknown". In
principle, any string could be hidden by such an [UNK]. Indeed, in information
retrieval, pretokenizers were themselves used as tokenizers (and also called
"tokenizers") with a word-level vocabulary that contained an [UNK].

Commonly used subword tokenization algorithms are [byte pair
encoding](/wiki/Byte_pair_encoding "Byte pair encoding") (BPE) and the unigram
language model (ULM), which each include a vocabularization algorithm and a
dedicated segmentation algorithm. There also exist several segmentation
algorithms that require no learning and can be applied given a vocabulary
(produced by BPE or ULM, for example), like greedily recognising tokens in a
pretoken by moving through it left-to-right. Well-known software
implementations of subword tokenizers are [Hugging Face](/wiki/Hugging_Face
"Hugging Face")'s `tokenizers` Python package implemented in Rust, and the
`sentencepiece` Python package implemented in C++. The latter package is named
as such because one of its configuration options allows disabling the built-in
pretokenizer, hence effectively making entire sentences a pretoken and thus
having the tokenizer see entire sentences, rather than individual words.

### Embedding

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=12
"Edit section: Embedding")]

Further information: [Word embedding](/wiki/Word_embedding "Word embedding")

Each integer token identifier is converted into an embedding vector via a
[lookup table](/wiki/Lookup_table "Lookup table"). Equivalently stated, it
multiplies a [one-hot](/wiki/One-hot "One-hot") representation of the token
identifier by an embedding matrix  M {\displaystyle M} ![{\\displaystyle
M}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f82cade9898ced02fdd08712e5f0c0151758a0dd).
For example, if the input token's identifier is  3 {\displaystyle 3}
![{\\displaystyle
3}](https://wikimedia.org/api/rest_v1/media/math/render/svg/991e33c6e207b12546f15bdfee8b5726eafbbb2f),
then the one-hot representation is  [ 0 , 0 , 0 , 1 , 0 , 0 , … ]
{\displaystyle [0,0,0,1,0,0,\dots ]} ![{\\displaystyle \[0,0,0,1,0,0,\\dots
\]}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a5a20e2ecac4d6b6e2e9fa0f965758e488c1d70f),
and its embedding vector is E m b e d ( 3 ) = [ 0 , 0 , 0 , 1 , 0 , 0 , … ] M
{\displaystyle \mathrm {Embed} (3)=[0,0,0,1,0,0,\dots ]M} ![{\\displaystyle
\\mathrm {Embed} \(3\)=\[0,0,0,1,0,0,\\dots
\]M}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66ba0293d96eeea4e56e92c73333349bc813855c)The
token embedding vectors are added to their respective positional encoding
vectors (see below), producing the sequence of input vectors.

The dimension of an embedding vector is called _hidden size_ or _embedding
size_ and written as  d emb {\displaystyle d_{\text{emb}}} ![{\\displaystyle
d_{\\text{emb}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4bf3df2909758ee1d69be67380da3263cfba984e).[35]
This size is written as  d model {\displaystyle d_{\text{model}}}
![{\\displaystyle
d_{\\text{model}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/aefdfb00976a3a5c5ec3c8fcbcc166e82ceb6268)
in the original transformer paper.[1]

### Un-embedding

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=13
"Edit section: Un-embedding")]

An un-embedding layer is almost the reverse of an embedding layer. Whereas an
embedding layer converts a token identifier into a vector, an un-embedding
layer converts a vector into a probability distribution over tokens.

The un-embedding layer is a linear-[softmax](/wiki/Softmax_function "Softmax function") layer: U n E m b e d ( x ) = s o f t m a x ( x W + b ) {\displaystyle \mathrm {UnEmbed} (x)=\mathrm {softmax} (xW+b)} ![{\\displaystyle \\mathrm {UnEmbed} \(x\)=\\mathrm {softmax} \(xW+b\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/df5d49f6baaf8081c203cd3613765a48f0a23da5)The matrix has shape  ( d emb , | V | ) {\displaystyle (d_{\text{emb}},|V|)} ![{\\displaystyle \(d_{\\text{emb}},|V|\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9dcb9b66af8f800d469cf5dfeb06c64ffbf2ab59). Some architectures use the transpose of the embedding matrix  M {\displaystyle M} ![{\\displaystyle M}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f82cade9898ced02fdd08712e5f0c0151758a0dd) as the un-embedding matrix  W {\displaystyle W} ![{\\displaystyle W}](https://wikimedia.org/api/rest_v1/media/math/render/svg/54a9c4c547f4d6111f81946cad242b18298d70b7) in order to avoid needing double the amount of embedding-related parameters and to avoid divergence during training. This practice is called _weight tying_.[52]

### Positional encoding

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=14
"Edit section: Positional encoding")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/0/02/Positional_encoding.png/250px-
Positional_encoding.png)](/wiki/File:Positional_encoding.png)A diagram of a
[sinusoidal](/wiki/Sine_wave "Sine wave") positional encoding with parameters
N = 10000 , d = 100 {\displaystyle N=10000,d=100} ![{\\displaystyle
N=10000,d=100}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fe83017b9728026bf6d2bae4a357041d198ac494)

A positional encoding is a fixed-size vector representation of the relative
positions of tokens within a sequence: it provides the transformer model with
information about _where_ the words are in the input sequence. This induces a
[bias](/wiki/Inductive_bias "Inductive bias") towards the order of the input
sequence, so that, for example, the input sequence "[man bites
dog](/wiki/Man_bites_dog "Man bites dog")" is processed differently from "dog
bites man".

The positional encoding is defined as a function of type  f : R -> R d
{\displaystyle f:\mathbb {R} \to \mathbb {R} ^{d}} ![{\\displaystyle
f:\\mathbb {R} \\to \\mathbb {R}
^{d}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ff4df0a644d47d52c00ba8ca23edbabb9c8c4749),
where  d {\displaystyle d} ![{\\displaystyle
d}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e85ff03cbe0c7341af6b982e47e9f90d235c66ab)
is a positive even [integer](/wiki/Integer "Integer"). The full positional
encoding defined in the original paper[1] is: ( f ( t ) 2 k , f ( t ) 2 k + 1
) = ( sin ⁡ ( θ ) , cos ⁡ ( θ ) ) ∀ k ∈ { 0 , 1 , … , d / 2 − 1 }
{\displaystyle (f(t)_{2k},f(t)_{2k+1})=(\sin(\theta ),\cos(\theta ))\quad
\forall k\in \\{0,1,\ldots ,d/2-1\\}} ![{\\displaystyle
\(f\(t\)_{2k},f\(t\)_{2k+1}\)=\(\\sin\(\\theta \),\\cos\(\\theta \)\)\\quad
\\forall k\\in \\{0,1,\\ldots
,d/2-1\\}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cbca45061217292a4920ea20881b77a1b39a41ea)where
θ = t r k , r = N 2 / d {\displaystyle \theta ={\frac {t}{r^{k}}},r=N^{2/d}}
![{\\displaystyle \\theta ={\\frac
{t}{r^{k}}},r=N^{2/d}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8ba16328b4d94e923d80ad257002a6d18deb2edb).

Here,  N {\displaystyle N} ![{\\displaystyle
N}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5e3890c981ae85503089652feb48b191b57aae3)
is a free parameter that should be significantly larger than the biggest  k
{\displaystyle k} ![{\\displaystyle
k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40)
that would be input into the positional encoding function. The original paper
uses  N = 10000 {\displaystyle N=10000} ![{\\displaystyle
N=10000}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8f13b17e1a7fbe046ab619ccc5167809d04872c2).

The function is in a simpler form when written as a complex function of type
f : R -> C d / 2 {\displaystyle f:\mathbb {R} \to \mathbb {C} ^{d/2}}
![{\\displaystyle f:\\mathbb {R} \\to \\mathbb {C}
^{d/2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/52c816b7a3f4f0855fc1cc7bafb9dbce1efc09d0)
f ( t ) = ( e i t / r k ) k = 0 , 1 , … , d 2 − 1 {\displaystyle
f(t)=\left(e^{it/r^{k}}\right)_{k=0,1,\ldots ,{\frac {d}{2}}-1}}
![{\\displaystyle f\(t\)=\\left\(e^{it/r^{k}}\\right\)_{k=0,1,\\ldots ,{\\frac
{d}{2}}-1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4887fec07bd9ef29ad5783f32651b1e503a88130)where
r = N 2 / d {\displaystyle r=N^{2/d}} ![{\\displaystyle
r=N^{2/d}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/11cb2cfb2ab25e2e0cb3ed51071f1e7f38060c99).

The main reason for using this positional encoding function is that using it,
shifts are linear transformations: f ( t + Δ t ) = d i a g ( f ( Δ t ) ) f ( t
) {\displaystyle f(t+\Delta t)=\mathrm {diag} (f(\Delta t))f(t)}
![{\\displaystyle f\(t+\\Delta t\)=\\mathrm {diag} \(f\(\\Delta
t\)\)f\(t\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cce4053e6d0f3e225b153bc362be4970c3e9b535)where
Δ t ∈ R {\displaystyle \Delta t\in \mathbb {R} } ![{\\displaystyle \\Delta
t\\in \\mathbb {R}
}](https://wikimedia.org/api/rest_v1/media/math/render/svg/40be374d0e9f96fefe0a14ddb46218a42409b2a6)
is the distance one wishes to shift. This allows the transformer to take any
encoded position, and find the encoding of the position n-steps-ahead or
n-steps-behind, by a matrix multiplication.

By taking a linear sum, any convolution can also be implemented as linear
transformations: ∑ j c j f ( t + Δ t j ) = ( ∑ j c j d i a g ( f ( Δ t j ) ) )
f ( t ) {\displaystyle \sum _{j}c_{j}f(t+\Delta t_{j})=\left(\sum
_{j}c_{j}\,\mathrm {diag} (f(\Delta t_{j}))\right)f(t)} ![{\\displaystyle
\\sum _{j}c_{j}f\(t+\\Delta t_{j}\)=\\left\(\\sum _{j}c_{j}\\,\\mathrm {diag}
\(f\(\\Delta
t_{j}\)\)\\right\)f\(t\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/14a5ba5df2e142a7c6812dd345b2001550cfa3f0)for
any constants  c j {\displaystyle c_{j}} ![{\\displaystyle
c_{j}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a844d180d176af828d1636d4e85aa534d0b77baa).
This allows the transformer to take any encoded position and find a linear sum
of the encoded locations of its neighbors. This sum of encoded positions, when
fed into the attention mechanism, would create attention weights on its
neighbors, much like what happens in a [convolutional neural
network](/wiki/Convolutional_neural_network "Convolutional neural network")
[language model](/wiki/Language_model "Language model"). In the author's
words, "we hypothesized it would allow the model to easily learn to attend by
relative position."

In typical implementations, all operations are done over the real numbers, not
the complex numbers, but since [complex multiplication can be implemented as
real 2-by-2 matrix
multiplication](/wiki/Complex_number#Matrix_representation_of_complex_numbers
"Complex number"), this is a mere notational difference.

### Encoder–decoder (overview)

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=15
"Edit section: Encoder–decoder \(overview\)")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/5/53/Transformer%2C_one_encoder-
decoder_block.png/250px-Transformer%2C_one_encoder-
decoder_block.png)](/wiki/File:Transformer,_one_encoder-decoder_block.png)One
encoder–decoder block
[![](//upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Transformer%2C_stacked_layers_and_sublayers.png/250px-
Transformer%2C_stacked_layers_and_sublayers.png)](/wiki/File:Transformer,_stacked_layers_and_sublayers.png)A
transformer is composed of stacked encoder layers and decoder layers.

Like earlier [seq2seq](/wiki/Seq2seq "Seq2seq") models, the original
transformer model used an **encoder–decoder** architecture. The encoder
consists of encoding layers that process all the input tokens together one
layer after another, while the decoder consists of decoding layers that
iteratively process the encoder's output and the decoder's output tokens so
far.

The purpose of each encoder layer is to create contextualized representations
of the tokens, where each representation corresponds to a token that "mixes"
information from other input tokens via self-attention mechanism. Each decoder
layer contains two attention sublayers: (1) cross-attention for incorporating
the output of encoder (contextualized input token representations), and (2)
self-attention for "mixing" information among the input tokens to the decoder
(i.e. the tokens generated so far during inference time).[53][54]

Both the encoder and decoder layers have a [feed-forward neural
network](/wiki/Feedforward_neural_network "Feedforward neural network") for
additional processing of their outputs and contain residual connections and
layer normalization steps.[54] These feed-forward layers contain most of the
parameters in a transformer model.

### Feedforward network

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=16
"Edit section: Feedforward network")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/5/59/Transformer_architecture_-
_FFN_module.png/250px-Transformer_architecture_-
_FFN_module.png)](/wiki/File:Transformer_architecture_-_FFN_module.png)The
feedforward network module. It is a two-layered network that maps  d emb
{\displaystyle d_{\text{emb}}} ![{\\displaystyle
d_{\\text{emb}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4bf3df2909758ee1d69be67380da3263cfba984e)-dimensional
vectors into  d emb {\displaystyle d_{\text{emb}}} ![{\\displaystyle
d_{\\text{emb}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4bf3df2909758ee1d69be67380da3263cfba984e)-dimensional
vectors.

The feedforward network (FFN) modules in a transformer are 2-layered
[multilayer perceptrons](/wiki/Feedforward_neural_network "Feedforward neural
network"): F F N ( x ) = ϕ ( x W ( 1 ) + b ( 1 ) ) W ( 2 ) + b ( 2 )
{\displaystyle \mathrm {FFN} (x)=\phi (xW^{(1)}+b^{(1)})W^{(2)}+b^{(2)}}
![{\\displaystyle \\mathrm {FFN} \(x\)=\\phi
\(xW^{\(1\)}+b^{\(1\)}\)W^{\(2\)}+b^{\(2\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3018d1cafd676461ec6a1927aff651d73ce78377)where
W ( 1 ) {\displaystyle W^{(1)}} ![{\\displaystyle
W^{\(1\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/351c8e7ea5512879f0b5762c284792c760b4a70e)
and  W ( 2 ) {\displaystyle W^{(2)}} ![{\\displaystyle
W^{\(2\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2196a6b93c1ae79e6b2b6cbe9c6c411cf1420513)
are weight matrices and  b ( 1 ) {\displaystyle b^{(1)}} ![{\\displaystyle
b^{\(1\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6abb02f6ce2b97279afa53deca31b9436df25421)
and  b ( 2 ) {\displaystyle b^{(2)}} ![{\\displaystyle
b^{\(2\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3b10499e26db8834d9306ad4deb7f1a095e8ff27)
are bias vectors, and  ϕ {\displaystyle \phi } ![{\\displaystyle \\phi
}](https://wikimedia.org/api/rest_v1/media/math/render/svg/72b1f30316670aee6270a28334bdf4f5072cdde4)
is its activation function. The original transformer used
[ReLU](/wiki/Rectifier_\(neural_networks\) "Rectifier \(neural networks\)")
activation.

The number of neurons in the middle layer is called _intermediate size_
(GPT),[55] _filter size_ (BERT),[35] or _feedforward size_ (BERT).[35] It is
typically larger than the embedding size. For example, in both GPT-2 series
and BERT series, the intermediate size of a model is 4 times its embedding
size:  d ffn = 4 d emb {\displaystyle d_{\text{ffn}}=4d_{\text{emb}}}
![{\\displaystyle
d_{\\text{ffn}}=4d_{\\text{emb}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/11c9e89a82cdff80cd9e03abfef22730a29bf958).

### Scaled dot-product attention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=17
"Edit section: Scaled dot-product attention")]

Main article: [Dot-product attention](/wiki/Dot-product_attention "Dot-product
attention")

#### Attention head

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=18
"Edit section: Attention head")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Transformer%2C_attention_block_diagram.png/250px-
Transformer%2C_attention_block_diagram.png)](/wiki/File:Transformer,_attention_block_diagram.png)Scaled
dot-product attention, block diagram
[![](//upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Transformer_architecture_-
_Attention_Head_module.png/250px-Transformer_architecture_-
_Attention_Head_module.png)](/wiki/File:Transformer_architecture_-
_Attention_Head_module.png)Exact dimension counts within an attention head
module

The attention mechanism used in the transformer architecture are scaled [dot-
product](/wiki/Dot_product "Dot product")
[attention](/wiki/Attention_\(machine_learning\) "Attention \(machine
learning\)") units. For each unit, the transformer model learns three weight
matrices: the query weights  W Q {\displaystyle W^{Q}} ![{\\displaystyle
W^{Q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/12fad024825b554ffb621d5385460ffce533f1bb),
the key weights  W K {\displaystyle W^{K}} ![{\\displaystyle
W^{K}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/060b854f3f44615cefb8441780e6c31742f5dbd2),
and the value weights  W V {\displaystyle W^{V}} ![{\\displaystyle
W^{V}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ef0a2e5fb27e9e6d1fc86901833d40d7e685a460).

The module takes three sequences, a query sequence, a key sequence, and a
value sequence. The query sequence is a sequence of length  ℓ seq, query
{\displaystyle \ell _{\text{seq, query}}} ![{\\displaystyle \\ell
_{\\text{seq,
query}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fe514b95a8db1105db6bcdf5a7148d8014461e59),
and each entry is a vector of dimension  d emb, query {\displaystyle
d_{\text{emb, query}}} ![{\\displaystyle d_{\\text{emb,
query}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/569324b1ee8814a09242042f2fffdbac51e922bd).
Similarly for the key and value sequences.

For each vector  x i , query {\displaystyle x_{i,{\text{query}}}}
![{\\displaystyle
x_{i,{\\text{query}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0d096bf3997e6d4d12626058f5747fa4a19f0ca8)
in the query sequence, it is multiplied by a matrix  W Q {\displaystyle W^{Q}}
![{\\displaystyle
W^{Q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/12fad024825b554ffb621d5385460ffce533f1bb)
to produce a query vector  q i = x i , query W Q {\displaystyle
q_{i}=x_{i,{\text{query}}}W^{Q}} ![{\\displaystyle
q_{i}=x_{i,{\\text{query}}}W^{Q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ad0056fecb11a213583cff46a83e331050830a13).
The matrix of all query vectors is the query matrix: Q = X query W Q
{\displaystyle Q=X_{\text{query}}W^{Q}} ![{\\displaystyle
Q=X_{\\text{query}}W^{Q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/1fdcfa516a1e0a158286801715d89368d2d8a948)Similarly,
we construct the key matrix  K = X key W K {\displaystyle
K=X_{\text{key}}W^{K}} ![{\\displaystyle
K=X_{\\text{key}}W^{K}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/25cdd16edf96b2453753c8d73d9b86bd7acee034)
and the value matrix  V = X value W V {\displaystyle V=X_{\text{value}}W^{V}}
![{\\displaystyle
V=X_{\\text{value}}W^{V}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4a44f4ff55f3ba2722b925af1e749c37936c88a6).

It is usually the case that all  W Q , W K , W V {\displaystyle
W^{Q},W^{K},W^{V}} ![{\\displaystyle
W^{Q},W^{K},W^{V}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5c6380cb67a00550ee5dfb91733a9bfdad94b42)
are square matrices, meaning  d emb, query = d query {\displaystyle
d_{\text{emb, query}}=d_{\text{query}}} ![{\\displaystyle d_{\\text{emb,
query}}=d_{\\text{query}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ed9f9eea42977c0cab83ddcf2f1de48138e007c6),
etc.

Attention weights are calculated using the query and key vectors: the
attention weight  a i j {\displaystyle a_{ij}} ![{\\displaystyle
a_{ij}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ebea6cd2813c330c798921a2894b358f7b643917)
from token  i {\displaystyle i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)
to token  j {\displaystyle j} ![{\\displaystyle
j}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2f461e54f5c093e92a55547b9764291390f0b5d0)
is the [dot product](/wiki/Dot_product "Dot product") between  q i
{\displaystyle q_{i}} ![{\\displaystyle
q_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2752dcbff884354069fe332b8e51eb0a70a531b6)
and  k j {\displaystyle k_{j}} ![{\\displaystyle
k_{j}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/05ddf2c6d7759ac955e001a7cfafb2abfca41b0b).
The attention weights are divided by the square root of the dimension of the
key vectors,  d k {\displaystyle {\sqrt {d_{k}}}} ![{\\displaystyle {\\sqrt
{d_{k}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0be678d1b945828faecd56b29927f5a60011be37),
which stabilizes gradients during training, and passed through a
[softmax](/wiki/Softmax_function "Softmax function") which normalizes the
weights. The fact that  W Q {\displaystyle W^{Q}} ![{\\displaystyle
W^{Q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/12fad024825b554ffb621d5385460ffce533f1bb)
and  W K {\displaystyle W^{K}} ![{\\displaystyle
W^{K}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/060b854f3f44615cefb8441780e6c31742f5dbd2)
are different matrices allows attention to be non-symmetric: if token  i
{\displaystyle i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)
attends to token  j {\displaystyle j} ![{\\displaystyle
j}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2f461e54f5c093e92a55547b9764291390f0b5d0)
(i.e.  q i ⋅ k j {\displaystyle q_{i}\cdot k_{j}} ![{\\displaystyle
q_{i}\\cdot
k_{j}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7de4219a59ace005d92f8d0a13466dbdb5fd6d9c)
is large), this does not necessarily mean that token  j {\displaystyle j}
![{\\displaystyle
j}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2f461e54f5c093e92a55547b9764291390f0b5d0)
will attend to token  i {\displaystyle i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)
(i.e.  q j ⋅ k i {\displaystyle q_{j}\cdot k_{i}} ![{\\displaystyle
q_{j}\\cdot
k_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d40445a57203e20510d7b629e0567957524700e4)
could be small). The output of the attention unit for token  i {\displaystyle
i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)
is the weighted sum of the value vectors of all tokens, weighted by  a i j
{\displaystyle a_{ij}} ![{\\displaystyle
a_{ij}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ebea6cd2813c330c798921a2894b358f7b643917),
the attention from token  i {\displaystyle i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)
to each token.

The attention calculation for all tokens can be expressed as one large matrix
calculation using the [softmax function](/wiki/Softmax_function "Softmax
function"), which is useful for training due to computational matrix operation
optimizations that quickly compute matrix operations. The matrices  Q
{\displaystyle Q} ![{\\displaystyle
Q}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8752c7023b4b3286800fe3238271bbca681219ed),
K {\displaystyle K} ![{\\displaystyle
K}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b76fce82a62ed5461908f0dc8f037de4e3686b0)
and  V {\displaystyle V} ![{\\displaystyle
V}](https://wikimedia.org/api/rest_v1/media/math/render/svg/af0f6064540e84211d0ffe4dac72098adfa52845)
are defined as the matrices where the  i {\displaystyle i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)th
rows are vectors  q i {\displaystyle q_{i}} ![{\\displaystyle
q_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2752dcbff884354069fe332b8e51eb0a70a531b6),
k i {\displaystyle k_{i}} ![{\\displaystyle
k_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f29138ed3ad54ffce527daccadc49c520459b0b0),
and  v i {\displaystyle v_{i}} ![{\\displaystyle
v_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7dffe5726650f6daac54829972a94f38eb8ec127)
respectively. Then we can represent the attention as Attention ( Q , K , V ) =
softmax ( Q K T d k ) V {\displaystyle
{\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac
{QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\end{aligned}}} ![{\\displaystyle
{\\begin{aligned}{\\text{Attention}}\(Q,K,V\)={\\text{softmax}}\\left\({\\frac
{QK^{\\mathrm {T} }}{\\sqrt
{d_{k}}}}\\right\)V\\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0b2afc7240eb97375a384b1628c18438e3068e3f)

where the softmax is applied over each of the rows of the matrix.

The number of dimensions in a query vector is _query size_ d query
{\displaystyle d_{\text{query}}} ![{\\displaystyle
d_{\\text{query}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a08e7abd7e328c9458c6522b8c0746f27c2d8b53)
and similarly for the _key size_ d key {\displaystyle d_{\text{key}}}
![{\\displaystyle
d_{\\text{key}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fb86df1f34f41a6100f5569f3b0ab489a14b7136)
and _value size_ d value {\displaystyle d_{\text{value}}} ![{\\displaystyle
d_{\\text{value}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/046c86fdb216cdea1d8ee121df3b755763001ab1).
The output dimension of an attention head is its _head dimension_ d head
{\displaystyle d_{\text{head}}} ![{\\displaystyle
d_{\\text{head}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dc21fc3863abb48214d18eeb00efa0c3ae102896).
The attention mechanism requires the following three equalities to hold: ℓ
seq, key = ℓ seq, value , d query = d key , d value = d head {\displaystyle
\ell _{\text{seq, key}}=\ell _{\text{seq,
value}},\;d_{\text{query}}=d_{\text{key}},\;d_{\text{value}}=d_{\text{head}}}
![{\\displaystyle \\ell _{\\text{seq, key}}=\\ell _{\\text{seq,
value}},\\;d_{\\text{query}}=d_{\\text{key}},\\;d_{\\text{value}}=d_{\\text{head}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b25b25f22a8a09c26350d2f065628dd4b3911669)but
is otherwise unconstrained.

If the attention head is used in a self-attention fashion, then  X query = X
key = X value {\displaystyle X_{\text{query}}=X_{\text{key}}=X_{\text{value}}}
![{\\displaystyle
X_{\\text{query}}=X_{\\text{key}}=X_{\\text{value}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/05e0578cf40298283b50d5e5874308d529fc6ec7).
If the attention head is used in a cross-attention fashion, then usually  X
query ≠ X key = X value {\displaystyle X_{\text{query}}\neq
X_{\text{key}}=X_{\text{value}}} ![{\\displaystyle X_{\\text{query}}\\neq
X_{\\text{key}}=X_{\\text{value}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/398ed1ae2490d963661a8ae37d94c04bfc732f9f).
It is theoretically possible for all three to be different, but that is rarely
the case in practice.

#### Multihead attention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=19
"Edit section: Multihead attention")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Multiheaded_attention%2C_block_diagram.png/250px-
Multiheaded_attention%2C_block_diagram.png)](/wiki/File:Multiheaded_attention,_block_diagram.png)Multihead
attention, block diagram
[![](//upload.wikimedia.org/wikipedia/commons/thumb/1/15/Transformer_architecture_-
_Multiheaded_Attention_module.png/250px-Transformer_architecture_-
_Multiheaded_Attention_module.png)](/wiki/File:Transformer_architecture_-
_Multiheaded_Attention_module.png)Exact dimension counts within a multihead
attention module

One set of  ( W Q , W K , W V ) {\displaystyle \left(W^{Q},W^{K},W^{V}\right)}
![{\\displaystyle
\\left\(W^{Q},W^{K},W^{V}\\right\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/1306697728f261e1803778d1b2e042c7df652ae7)
matrices is called an _attention head_ , and each layer in a transformer model
has multiple attention heads. While each attention head attends to the tokens
that are relevant to each token, multiple attention heads allow the model to
do this for different definitions of "relevance". Specifically, the query and
key projection matrices,  W Q {\displaystyle W^{Q}} ![{\\displaystyle
W^{Q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/12fad024825b554ffb621d5385460ffce533f1bb)
and  W K {\displaystyle W^{K}} ![{\\displaystyle
W^{K}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/060b854f3f44615cefb8441780e6c31742f5dbd2)
, which are involved in the attention score computation, defines the
"relevance". Meanwhile, the value [projection matrix](/wiki/Projection_matrix
"Projection matrix") W V {\displaystyle W^{V}} ![{\\displaystyle
W^{V}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ef0a2e5fb27e9e6d1fc86901833d40d7e685a460),
in combination with the part of the output projection matrix  W O
{\displaystyle W^{O}} ![{\\displaystyle
W^{O}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7f0f376fd1863b3a195a6bf34b56ff43ec5d695f),
determines how the attended tokens influence what information is passed to
subsequent layers and ultimately the output logits. In addition, the scope of
attention, or the range of token relationships captured by each attention
head, can expand as tokens pass through successive layers. This allows the
model to capture more complex and long-range dependencies in deeper layers.
Many transformer attention heads encode relevance relations that are
meaningful to humans. For example, some attention heads can attend mostly to
the next word, while others mainly attend from verbs to their direct
objects.[56] The computations for each attention head can be performed in
[parallel](/wiki/Parallel_computing "Parallel computing"), which allows for
fast processing. The outputs for the attention layer are concatenated to pass
into the [feedforward neural network](/wiki/Feedforward_neural_network
"Feedforward neural network") layers.

Concretely, let the multiple attention heads be indexed by  i {\displaystyle
i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20),
then we have MultiheadAttention ( Q , K , V ) = Concat i ∈ [ n heads ] (
Attention ( X W i Q , X W i K , X W i V ) ) W O {\displaystyle
{\text{MultiheadAttention}}(Q,K,V)={\text{Concat}}_{i\in
[n_{\text{heads}}]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}}
![{\\displaystyle
{\\text{MultiheadAttention}}\(Q,K,V\)={\\text{Concat}}_{i\\in
\[n_{\\text{heads}}\]}\({\\text{Attention}}\(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}\)\)W^{O}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/266365c28eb10c53cf80eb9703447d3a8233414d)
where the matrix  X {\displaystyle X} ![{\\displaystyle
X}](https://wikimedia.org/api/rest_v1/media/math/render/svg/68baa052181f707c662844a465bfeeb135e82bab)
is the concatenation of word embeddings, and the matrices  W i Q , W i K , W i
V {\displaystyle W_{i}^{Q},W_{i}^{K},W_{i}^{V}} ![{\\displaystyle
W_{i}^{Q},W_{i}^{K},W_{i}^{V}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3087f1739ddc134719d701163d3a75af985498b1)
are "projection matrices" owned by individual attention head  i {\displaystyle
i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20),
and  W O {\displaystyle W^{O}} ![{\\displaystyle
W^{O}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7f0f376fd1863b3a195a6bf34b56ff43ec5d695f)
is a final projection matrix owned by the whole multihead attention head.

It is theoretically possible for each attention head to have a different head
dimension  d head {\displaystyle d_{\text{head}}} ![{\\displaystyle
d_{\\text{head}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dc21fc3863abb48214d18eeb00efa0c3ae102896),
but that is rarely the case in practice.

As an example, in the smallest GPT-2 model, there are only self-attention
mechanisms. It has the following dimensions: d emb = 768 , n head = 12 , d
head = 64 {\displaystyle
d_{\text{emb}}=768,n_{\text{head}}=12,d_{\text{head}}=64} ![{\\displaystyle
d_{\\text{emb}}=768,n_{\\text{head}}=12,d_{\\text{head}}=64}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dd3bb7b2294f3753ad86ffa754b8840b002bd63f)Since
12 × 64 = 768 {\displaystyle 12\times 64=768} ![{\\displaystyle 12\\times
64=768}](https://wikimedia.org/api/rest_v1/media/math/render/svg/27d429c67c8d2bb230091a87d8f4b000de427bb3),
its output projection matrix  W O ∈ R ( 12 × 64 ) × 768 {\displaystyle
W^{O}\in \mathbb {R} ^{(12\times 64)\times 768}} ![{\\displaystyle W^{O}\\in
\\mathbb {R} ^{\(12\\times 64\)\\times
768}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/be9cea988019d5b7d190ec9592f3c7912eb5efd9)
is a square matrix.

#### Masked attention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=20
"Edit section: Masked attention")]

The transformer architecture is constructed to calculate output tokens
iteratively. Assuming  t = 0 {\displaystyle t=0} ![{\\displaystyle
t=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/43469ec032d858feae5aa87029e22eaaf0109e9c)
refers to the calculation of the first output token  i = 0 {\displaystyle i=0}
![{\\displaystyle
i=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/31a682d568ee6a5fe51d76423186057f625ada5c),
for step  t > 0 {\displaystyle t>0} ![{\\displaystyle
t>0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/29a2960e88369263fe3cfe00ccbfeb83daee212a),
the output token  i = 0 {\displaystyle i=0} ![{\\displaystyle
i=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/31a682d568ee6a5fe51d76423186057f625ada5c)
shall remain constant. This ensures properties of the model similar to
[autoregressive models](/wiki/Autoregressive_models "Autoregressive
models").[1] Therefore, at every time step  t {\displaystyle t}
![{\\displaystyle
t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560),
the calculation for all outputs  i {\displaystyle i} ![{\\displaystyle
i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20)
should not have access to tokens at position  j {\displaystyle j}
![{\\displaystyle
j}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2f461e54f5c093e92a55547b9764291390f0b5d0)
for  j >= i {\displaystyle j>=i} ![{\\displaystyle
j>=i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0962580a4b2002cf7038e5f3529763c32044a040)
(as it naturally is the case for time step  t = i {\displaystyle t=i}
![{\\displaystyle
t=i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/211e2471862f32d3a3ab7718688b739056c20adc),
when tokens  j > t {\displaystyle j>t} ![{\\displaystyle
j>t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8b16985b39fa0ca2efcd29a2ea745312c6ee7915)
are not yet calculated). This behavior may be accomplished before the softmax
stage by adding a mask matrix  M {\displaystyle M} ![{\\displaystyle
M}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f82cade9898ced02fdd08712e5f0c0151758a0dd)
that is  − ∞ {\displaystyle -\infty } ![{\\displaystyle -\\infty
}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ca2608c4b5fd3bffc73585f8c67e379b4e99b6f1)
at entries where the attention link must be cut, and  0 {\displaystyle 0}
![{\\displaystyle
0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2aae8864a3c1fec9585261791a809ddec1489950)
at other places: MaskedAttention ( Q , K , V ) = softmax ( M + Q K T d k ) V
{\displaystyle
{\begin{aligned}{\text{MaskedAttention}}(Q,K,V)={\text{softmax}}\left(M+{\frac
{QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\end{aligned}}} ![{\\displaystyle
{\\begin{aligned}{\\text{MaskedAttention}}\(Q,K,V\)={\\text{softmax}}\\left\(M+{\\frac
{QK^{\\mathrm {T} }}{\\sqrt
{d_{k}}}}\\right\)V\\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8d99a80dbf8da6e52c37ba3c9965387a19f82975)
The following matrix is commonly used in decoder self-attention modules,
called "causal masking": M causal = [ 0 − ∞ − ∞ … − ∞ 0 0 − ∞ … − ∞ 0 0 0 … −
∞ ⋮ ⋮ ⋮ ⋱ ⋮ 0 0 0 … 0 ] {\displaystyle
M_{\text{causal}}={\begin{bmatrix}0&-\infty &-\infty &\dots &-\infty
\\\0&0&-\infty &\dots &-\infty \\\0&0&0&\dots &-\infty \\\\\vdots &\vdots
&\vdots &\ddots &\vdots \\\0&0&0&\dots &0\end{bmatrix}}} ![{\\displaystyle
M_{\\text{causal}}={\\begin{bmatrix}0&-\\infty &-\\infty &\\dots &-\\infty
\\\\0&0&-\\infty &\\dots &-\\infty \\\\0&0&0&\\dots &-\\infty \\\\\\vdots
&\\vdots &\\vdots &\\ddots &\\vdots \\\\0&0&0&\\dots
&0\\end{bmatrix}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/981c71d86645b9f71d314dc671903905c0c30a9a)

In words, it means that each token can pay attention to itself, and every
token before it, but not any after it. A non-masked attention module can be
thought of as a masked attention module where the mask has all entries zero.
As an example of an uncommon use of mask matrix, the [XLNet](/wiki/XLNet
"XLNet") considers all masks of the form  P M causal P − 1 {\displaystyle
PM_{\text{causal}}P^{-1}} ![{\\displaystyle
PM_{\\text{causal}}P^{-1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/08430a7d86ac20f4e73548c704aff43512d88f46),
where  P {\displaystyle P} ![{\\displaystyle
P}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b4dc73bf40314945ff376bd363916a738548d40a)
is a random [permutation matrix](/wiki/Permutation_matrix "Permutation
matrix").[57]

### Encoder

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=21
"Edit section: Encoder")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Transformer%2C_one_encoder_block.png/250px-
Transformer%2C_one_encoder_block.png)](/wiki/File:Transformer,_one_encoder_block.png)One
encoder layer

An encoder consists of an embedding layer, followed by multiple encoder
layers.

Each encoder layer consists of two major components: a self-attention
mechanism and a feed-forward layer. It takes an input as a sequence of input
vectors, applies the self-attention mechanism, to produce an intermediate
sequence of vectors, then applies the feed-forward layer for each vector
individually. Schematically, we have: given input vectors h 0 , h 1 , …
combine them into a matrix H = [ h 0 h 1 ⋮ ] EncoderLayer ( H ) = [ FFN (
MultiheadAttention ( H , H , H ) 0 ) FFN ( MultiheadAttention ( H , H , H ) 1
) ⋮ ] {\displaystyle {\begin{aligned}{\text{given input vectors
}}&h_{0},h_{1},\dots \\\\{\text{combine them into a matrix
}}H&={\begin{bmatrix}h_{0}\\\h_{1}\\\\\vdots
\end{bmatrix}}\\\\{\text{EncoderLayer}}(H)&={\begin{bmatrix}{\text{FFN}}({\text{MultiheadAttention}}(H,H,H)_{0})\\\\{\text{FFN}}({\text{MultiheadAttention}}(H,H,H)_{1})\\\\\vdots
\end{bmatrix}}\\\\\end{aligned}}} ![{\\displaystyle
{\\begin{aligned}{\\text{given input vectors }}&h_{0},h_{1},\\dots
\\\\{\\text{combine them into a matrix
}}H&={\\begin{bmatrix}h_{0}\\\\h_{1}\\\\\\vdots
\\end{bmatrix}}\\\\{\\text{EncoderLayer}}\(H\)&={\\begin{bmatrix}{\\text{FFN}}\({\\text{MultiheadAttention}}\(H,H,H\)_{0}\)\\\\{\\text{FFN}}\({\\text{MultiheadAttention}}\(H,H,H\)_{1}\)\\\\\\vdots
\\end{bmatrix}}\\\\\\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fd9a9a11a953fbb54e9a41092b2fd5e0e04da7e8)

where  FFN {\displaystyle {\text{FFN}}} ![{\\displaystyle
{\\text{FFN}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ad653c6de611b65e2c8f58ac99a27bb4406b1ed8)
stands for "feed-forward network". We can more succinctly write it as
EncoderLayer ( H ) = FFN ( MultiheadAttention ( H , H , H ) ) {\displaystyle
{\text{EncoderLayer}}(H)={\text{FFN}}({\text{MultiheadAttention}}(H,H,H))}
![{\\displaystyle
{\\text{EncoderLayer}}\(H\)={\\text{FFN}}\({\\text{MultiheadAttention}}\(H,H,H\)\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6c181dfb3b1a62638c2a05462827bbe405dc63d7)with
the implicit convention that the  FFN {\displaystyle {\text{FFN}}}
![{\\displaystyle
{\\text{FFN}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ad653c6de611b65e2c8f58ac99a27bb4406b1ed8)
is applied to each row of the matrix individually.

The encoder layers are stacked. The first encoder layer takes the sequence of
input vectors from the embedding layer, producing a sequence of vectors. This
sequence of vectors is processed by the second encoder, and so on. The output
from the final encoder layer is then used by the decoder.

As the encoder processes the entire input all at once, every token can attend
to every other token (all-to-all attention), so there is no need for causal
masking.

### Decoder

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=22
"Edit section: Decoder")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/5/55/Transformer%2C_one_decoder_block.png/250px-
Transformer%2C_one_decoder_block.png)](/wiki/File:Transformer,_one_decoder_block.png)One
decoder layer

A decoder consists of an embedding layer, followed by multiple decoder layers,
followed by an un-embedding layer.

Each decoder consists of three major components: a causally masked self-
attention mechanism, a cross-attention mechanism, and a feed-forward neural
network. The decoder functions in a similar fashion to the encoder, but an
additional attention mechanism is inserted which instead draws relevant
information from the encodings generated by the encoders. This mechanism can
also be called the _encoder–decoder attention_.[1][54]

Like the first encoder, the first decoder takes positional information and
embeddings of the output sequence as its input, rather than encodings. The
transformer must not use the current or future output to predict an output, so
the output sequence must be partially masked to prevent this reverse
information flow.[1] This allows for
[autoregressive](/wiki/Autoregressive_model "Autoregressive model") text
generation. For decoding, all-to-all attention is inappropriate, because a
token cannot attend to tokens not yet generated. Thus, the self-attention
module in the decoder is causally masked.

In contrast, the cross-attention mechanism attends to the output vectors of
the encoder, which is computed before the decoder starts decoding.
Consequently, there is no need for masking in the cross-attention mechanism.

Schematically, we have: H ′ = MaskedMultiheadAttention ( H , H , H )
DecoderLayer ( H ) = FFN ( MultiheadAttention ( H ′ , H E , H E ) )
{\displaystyle
{\begin{aligned}H'&={\text{MaskedMultiheadAttention}}(H,H,H)\\\\{\text{DecoderLayer}}(H)&={\text{FFN}}({\text{MultiheadAttention}}(H',H^{E},H^{E}))\end{aligned}}}
![{\\displaystyle
{\\begin{aligned}H'&={\\text{MaskedMultiheadAttention}}\(H,H,H\)\\\\{\\text{DecoderLayer}}\(H\)&={\\text{FFN}}\({\\text{MultiheadAttention}}\(H',H^{E},H^{E}\)\)\\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7be5264b442c0f99ef6d3c6e8a8bccf78902ade6)where
H E {\displaystyle H^{E}} ![{\\displaystyle
H^{E}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ca07d5c8fe45403067683c7e75a5e1e50d461dea)
is the matrix with rows being the output vectors from the encoder.

The last decoder is followed by a final un-embedding layer to produce the
output probabilities over the vocabulary. Then, one of the tokens is sampled
according to the probability, and the decoder can be run again to produce the
next token, etc., autoregressively generating output text.

### Adapted architectures

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=23
"Edit section: Adapted architectures")]

Many [large language models](/wiki/Large_language_models "Large language
models"), since they do not need to predict a whole new sequence from an input
sequence, only use the encoder or decoder of the original transformer
architecture. Early [GPT](/wiki/Generative_pre-trained_transformer "Generative
pre-trained transformer") models are decoder-only models trained to predict
the next token in a sequence.[58] [BERT](/wiki/BERT_\(language_model\) "BERT
\(language model\)"), another language model, only makes use of an encoder,
and is trained to predict a randomly masked token in a sequence.[35]

## Full transformer architecture

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=24
"Edit section: Full transformer architecture")]

### Sublayers

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=25
"Edit section: Sublayers")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Transformer%2C_stacked_multilayers.png/250px-
Transformer%2C_stacked_multilayers.png)](/wiki/File:Transformer,_stacked_multilayers.png)(a)
One encoder layer and one decoder layer. (b) Two encoder layers and two
decoder layers. The sublayers are labelled as well.

Each encoder layer contains 2 sublayers: the self-attention and the
feedforward network. Each decoder layer contains 3 sublayers: the causally
masked self-attention, the cross-attention, and the feedforward network.

[![](//upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Transformer_encoder%2C_with_norm-
first_and_norm-last.png/250px-Transformer_encoder%2C_with_norm-first_and_norm-
last.png)](/wiki/File:Transformer_encoder,_with_norm-first_and_norm-
last.png)Transformer encoder with norm-first and norm-last
[![](//upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Transformer_decoder%2C_with_norm-
first_and_norm-last.png/250px-Transformer_decoder%2C_with_norm-first_and_norm-
last.png)](/wiki/File:Transformer_decoder,_with_norm-first_and_norm-
last.png)Transformer decoder with norm-first and norm-last
[![](//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/250px-
Transformer%2C_full_architecture.png)](/wiki/File:Transformer,_full_architecture.png)Block
diagram for the full transformer
architecture[![](//upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Transformer%2C_schematic_object_hierarchy%2C_for_implementation_in_object-
oriented_programming.png/250px-
Transformer%2C_schematic_object_hierarchy%2C_for_implementation_in_object-
oriented_programming.png)](/wiki/File:Transformer,_schematic_object_hierarchy,_for_implementation_in_object-
oriented_programming.png)Schematic [object hierarchy](/wiki/Object_hierarchy
"Object hierarchy") for the full transformer architecture, in [object-oriented
programming](/wiki/Object-oriented_programming "Object-oriented programming")
style

The final points of detail are the [residual
connections](/wiki/Residual_neural_network "Residual neural network") and
[layer normalization](/wiki/Layer_normalization "Layer normalization"),
(denoted as "LayerNorm", or "LN" in the following), which while conceptually
unnecessary, are necessary for numerical stability and convergence.

The residual connection, which is introduced to avoid vanishing gradient
issues and stabilize the training process, can be expressed as follows: y =
F(x) + x. The expression indicates that an output y is the sum of the
transformation of input x (F(x)) and the input itself (x). Adding the input x
can preserve the input information and avoid issues when the gradient of F(x)
is close to zero.

Similarly to how the feedforward network modules are applied individually to
each vector, the LayerNorm is also applied individually to each vector.

There are two common conventions in use: the _post-LN_ and the _pre-LN_
convention. In the post-LN convention, the output of each sublayer is  L a y e
r N o r m ( x + S u b l a y e r ( x ) ) {\displaystyle \mathrm {LayerNorm}
(x+\mathrm {Sublayer} (x))} ![{\\displaystyle \\mathrm {LayerNorm}
\(x+\\mathrm {Sublayer}
\(x\)\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dbfd5ef346a396976d4b6cea30408e27192b4ca8)where
S u b l a y e r ( x ) {\displaystyle \mathrm {Sublayer} (x)} ![{\\displaystyle
\\mathrm {Sublayer}
\(x\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a8c8327dbca36935f9f5f157967e6df5603880c9)
is the function implemented by the sublayer itself.

In the pre-LN convention, the output of each sublayer is x + S u b l a y e r (
L a y e r N o r m ( x ) ) {\displaystyle x+\mathrm {Sublayer} (\mathrm
{LayerNorm} (x))} ![{\\displaystyle x+\\mathrm {Sublayer} \(\\mathrm
{LayerNorm}
\(x\)\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/14a098c27734ee53b1efbf41656e1797f9ed2874)The
original 2017 transformer used the post-LN convention. It was difficult to
train and required careful hyperparameter tuning and a "warm-up" in learning
rate, where it starts small and gradually increases. The pre-LN convention,
proposed several times in 2018,[59] was found to be easier to train, requiring
no warm-up, leading to faster convergence.[46]

### Pseudocode

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=26
"Edit section: Pseudocode")]

The following is the pseudocode for a standard pre-LN encoder–decoder
transformer, adapted from _Formal Algorithms for Transformers_[60]

    
    
    **input:** Encoder input t_e
           Decoder input t_d
    **output:** Array of probability distributions, with shape (decoder vocabulary size x length(decoder output sequence))
    
    /* encoder */
    z_e ← encoder.tokenizer(t_e)
    
    **for** **each** t **in** 1:length(z_e) **do**
        z_e[t] ← encoder.embedding(z_e[t]) + encoder.positional_embedding(t)
    
    **for** **each** l **in** 1:length(encoder.layers) **do**
        layer ← encoder.layers[l]
    
        /* first sublayer */
        z_e_copy ← copy(z_e)
        **for each** t **in** 1:length(z_e) **do**
            z_e[t] ← layer.layer_norm(z_e[t])
        z_e ← layer.multihead_attention(z_e, z_e, z_e)
        **for each** t **in** 1:length(z_e) **do**
            z_e[t] ← z_e[t] + z_e_copy[t]
    
        /* second sublayer */
        z_e_copy ← copy(z_e)
        **for each** t **in** 1:length(z_e) **do**
            z_e[t] ← layer.layer_norm(z_e[t])
        z_e ← layer.feedforward(z_e)
        **for each** t **in** 1:length(z_e) **do**
            z_e[t] ← z_e[t] + z_e_copy[t]
    
    **for each** t **in** 1:length(z_e) **do**
        z_e[t] ← encoder.final_layer_norm(z_e[t])
    
    /* decoder */
    z_d ← decoder.tokenizer(t_d)
    
    **for** **each** t **in** 1:length(z_d) **do**
        z_d[t] ← decoder.embedding(z_d[t]) + decoder.positional_embedding(t)
    
    **for** **each** l **in** 1:length(decoder.layers) **do**
            layer ← decoder.layers[l]
    
            /* first sublayer */
            z_d_copy ← copy(z_d)
            **for each** t **in** 1:length(z_d) **do**
                z_d[t] ← layer.layer_norm(z_d[t])
            z_d ← layer.masked_multihead_attention(z_d, z_d, z_d)
            **for each** t **in** 1:length(z_d) **do**
                z_d[t] ← z_d[t] + z_d_copy[t]
    
            /* second sublayer */
            z_d_copy ← copy(z_d)
            **for each** t **in** 1:length(z_d) **do**
                z_d[t] ← layer.layer_norm(z_d[t])
            z_d ← layer.multihead_attention(z_d, z_e, z_e) 
            **for each** i **in** 1:length(z_d) **do**
                z_d[t] ← z_d[t] + z_d_copy[t]
    
            /* third sublayer */
            z_d_copy ← copy(z_d)
            **for each** t **in** 1:length(z_d) **do**
                z_d[t] ← layer.layer_norm(z_d[t])
            z_d ← layer.feedforward(z_d)
            **for each** t **in** 1:length(z_d) **do**
                z_d[t] ← z_d[t] + z_d_copy[t]
    
    z_d ← decoder.final_layer_norm(z_d)
    
    output_distributions ← []
    **for each** t **in** 1:length(z_d) **do**
        output_distributions.append(decoder.unembed(z_d[t]))
    
    **return** output_distributions
    

### Terminology

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=27
"Edit section: Terminology")]

The transformer architecture, being modular, allows variations. Several common
variations are described here.[61]

An "encoder-only" transformer applies the encoder to map an input text into a
sequence of vectors that represent the input text. This is usually used for
text embedding and [representation learning](/wiki/Feature_learning "Feature
learning") for downstream applications. [BERT](/wiki/BERT_\(language_model\)
"BERT \(language model\)") is encoder-only. They are less often used
currently, as they were found to be not significantly better than training an
encoder–decoder transformer, then taking just the encoder.[51]

A "decoder-only" transformer is not literally decoder-only, since without an
encoder, the cross-attention mechanism has nothing to attend to. Thus, the
decoder layers in a decoder-only transformer is composed of just two
sublayers: the causally masked self-attention, and the feedforward network.
This is usually used for [text generation](/wiki/Natural_language_generation
"Natural language generation") and [instruction
following](/wiki/Large_language_model#Instruction_tuning "Large language
model"). The models in the [GPT series](/wiki/Generative_pre-
trained_transformer "Generative pre-trained transformer") and [Chinchilla
series](/wiki/Chinchilla_\(language_model\) "Chinchilla \(language model\)")
are decoder-only.

An "encoder–decoder" transformer is generally the same as the original
transformer, with 2 sublayers per encoder layer and 3 sublayers per decoder
layer, etc. They might have minor architectural improvements, such as
alternative activation functions, changing the location of normalization, etc.
This is also usually used for text generation and instruction following. The
models in the [T5 series](/wiki/T5_\(language_model\) "T5 \(language model\)")
are encoder–decoder.[61]

A "prefixLM" (prefix language model) is a decoder-only architecture, but with
prefix masking, which is different from causal masking. Specifically, it has
mask of the form[61]: Figure 3 M prefixLM = [ 0 − ∞ 0 M causal ]
{\displaystyle M_{\text{prefixLM}}={\begin{bmatrix}\mathbf {0} &-\infty
\\\\\mathbf {0} &M_{\text{causal}}\end{bmatrix}}} ![{\\displaystyle
M_{\\text{prefixLM}}={\\begin{bmatrix}\\mathbf {0} &-\\infty \\\\\\mathbf {0}
&M_{\\text{causal}}\\end{bmatrix}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/55dde3d4ea5e6d9e321ca34ebfdd37268558e1aa)where
the first columns correspond to the "prefix", and the subsequent columns
correspond to the autoregressively generated text based on the prefix. They
resemble encoder–decoder models, but has less "sparsity". Such models are
rarely used, though they are cited as theoretical possibilities and
benchmarked comparisons.[51]

There are also mixed seq2seq models. For example, in 2020, Google Translate
replaced the previous RNN-encoder–RNN-decoder model with a transformer-
encoder–RNN-decoder model, as transformer-based decoders did not appear to
significantly increase quality unlike the encoder, while the RNN decoder was
much faster.[37]

## Subsequent work

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=28
"Edit section: Subsequent work")]

### Alternative activation functions

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=29
"Edit section: Alternative activation functions")]

The original transformer uses [ReLU](/wiki/ReLU "ReLU") [activation
function](/wiki/Activation_function "Activation function"). Other activation
functions were developed. The [Llama series](/wiki/Llama_\(language_model\)
"Llama \(language model\)") and [PaLM](/wiki/PaLM "PaLM") used SwiGLU;[62]
both GPT-1 and BERT[35] used GELU.[63]

Alternative activation functions are often used in combination with [Gated
Linear Units](/wiki/Gated_Linear_Unit "Gated Linear Unit") in the feedforward
module.[62]

### Alternative normalizations

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=30
"Edit section: Alternative normalizations")]

The normalization used in the transformer can be different from LayerNorm. One
example is [RMSNorm](/wiki/RMSNorm "RMSNorm")[64] which is used in the [Llama
series](/wiki/Llama_\(language_model\) "Llama \(language model\)"). Other
examples include CapsuleNorm[65] ScaleNorm,[66] or FixNorm.[66]

### Alternative positional encodings

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=31
"Edit section: Alternative positional encodings")]

Transformers may use other positional encoding methods than sinusoidal.[67]

The original transformer paper reported using a learned positional
encoding,[68] but finding it not superior to the sinusoidal one.[1] Later,[69]
found that causal masking itself provides enough signal to a transformer
decoder that it can learn to implicitly perform absolute positional encoding
without the positional encoding module.

#### RoPE

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=32
"Edit section: RoPE")]

RoPE (rotary positional embedding),[70] is best explained by considering a
list of 2-dimensional vectors  [ ( x 1 ( 1 ) , x 1 ( 2 ) ) , ( x 2 ( 1 ) , x 2
( 2 ) ) , ( x 3 ( 1 ) , x 3 ( 2 ) ) , . . . ] {\displaystyle
[(x_{1}^{(1)},x_{1}^{(2)}),(x_{2}^{(1)},x_{2}^{(2)}),(x_{3}^{(1)},x_{3}^{(2)}),...]}
![{\\displaystyle
\[\(x_{1}^{\(1\)},x_{1}^{\(2\)}\),\(x_{2}^{\(1\)},x_{2}^{\(2\)}\),\(x_{3}^{\(1\)},x_{3}^{\(2\)}\),...\]}](https://wikimedia.org/api/rest_v1/media/math/render/svg/08b00c812263b798fed7b345975d49dbebdfada5).
Now pick some angle  θ {\displaystyle \theta } ![{\\displaystyle \\theta
}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6e5ab2664b422d53eb0c7df3b87e1360d75ad9af).
Then RoPE encoding is RoPE ( x m ( 1 ) , x m ( 2 ) , m ) = ( cos ⁡ m θ − sin ⁡
m θ sin ⁡ m θ cos ⁡ m θ ) ( x m ( 1 ) x m ( 2 ) ) = ( x m ( 1 ) cos ⁡ m θ − x
m ( 2 ) sin ⁡ m θ x m ( 2 ) cos ⁡ m θ + x m ( 1 ) sin ⁡ m θ ) {\displaystyle
{\text{RoPE}}{\big (}x_{m}^{(1)},x_{m}^{(2)},m{\big )}={\begin{pmatrix}\cos
m\theta &-\sin m\theta \\\\\sin m\theta &\cos m\theta
\end{pmatrix}}{\begin{pmatrix}x_{m}^{(1)}\\\x_{m}^{(2)}\\\\\end{pmatrix}}={\begin{pmatrix}x_{m}^{(1)}\cos
m\theta -x_{m}^{(2)}\sin m\theta \\\x_{m}^{(2)}\cos m\theta +x_{m}^{(1)}\sin
m\theta \\\\\end{pmatrix}}} ![{\\displaystyle {\\text{RoPE}}{\\big
\(}x_{m}^{\(1\)},x_{m}^{\(2\)},m{\\big \)}={\\begin{pmatrix}\\cos m\\theta
&-\\sin m\\theta \\\\\\sin m\\theta &\\cos m\\theta
\\end{pmatrix}}{\\begin{pmatrix}x_{m}^{\(1\)}\\\\x_{m}^{\(2\)}\\\\\\end{pmatrix}}={\\begin{pmatrix}x_{m}^{\(1\)}\\cos
m\\theta -x_{m}^{\(2\)}\\sin m\\theta \\\\x_{m}^{\(2\)}\\cos m\\theta
+x_{m}^{\(1\)}\\sin m\\theta
\\\\\\end{pmatrix}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0a15ebe8d780e084275a5115ab1bd66867b2df86)Equivalently,
if we write the 2-dimensional vectors as complex numbers  z m := x m ( 1 ) + i
x m ( 2 ) {\displaystyle z_{m}:=x_{m}^{(1)}+ix_{m}^{(2)}} ![{\\displaystyle
z_{m}:=x_{m}^{\(1\)}+ix_{m}^{\(2\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ed57dd02fd5aafea96a4ee28322e10ca6883249f),
then RoPE encoding is just multiplication by an angle: RoPE ( z m , m ) = e i
m θ z m {\displaystyle {\text{RoPE}}{\big (}z_{m},m{\big )}=e^{im\theta
}z_{m}} ![{\\displaystyle {\\text{RoPE}}{\\big \(}z_{m},m{\\big
\)}=e^{im\\theta
}z_{m}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/de13aa67381dcfbf189a2beca91c14aa914c1d62)For
a list of  2 n {\displaystyle 2n} ![{\\displaystyle
2n}](https://wikimedia.org/api/rest_v1/media/math/render/svg/134afa8ff09fdddd24b06f289e92e3a045092bd1)-dimensional
vectors, a RoPE encoder is defined by a sequence of angles  θ ( 1 ) , . . . ,
θ ( n ) {\displaystyle \theta ^{(1)},...,\theta ^{(n)}} ![{\\displaystyle
\\theta ^{\(1\)},...,\\theta
^{\(n\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cf7ced81707daa22c51c4294a84b3f9d14d30eef).
Then the RoPE encoding is applied to each pair of coordinates.

The benefit of RoPE is that the dot-product between two vectors depends on
their relative location only: RoPE ( x , m ) T RoPE ( y , n ) = RoPE ( x , m +
k ) T RoPE ( y , n + k ) {\displaystyle {\text{RoPE}}{\big (}x,m{\big
)}^{T}{\text{RoPE}}{\big (}y,n{\big )}={\text{RoPE}}{\big (}x,m+k{\big
)}^{T}{\text{RoPE}}{\big (}y,n+k{\big )}} ![{\\displaystyle
{\\text{RoPE}}{\\big \(}x,m{\\big \)}^{T}{\\text{RoPE}}{\\big \(}y,n{\\big
\)}={\\text{RoPE}}{\\big \(}x,m+k{\\big \)}^{T}{\\text{RoPE}}{\\big
\(}y,n+k{\\big
\)}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e31c0d3482350f84642a7ec384650ab781eda79d)
for any integer  k {\displaystyle k} ![{\\displaystyle
k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40).

#### ALiBi

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=33
"Edit section: ALiBi")]

ALiBi (Attention with Linear Biases)[71] is not a _replacement_ for the
positional encoder on the original transformer. Instead, it is an _additional_
positional encoder that is directly plugged into the attention mechanism.
Specifically, the ALiBi attention mechanism is Attention ( Q , K , V ) =
softmax ( Q K T d k + s B ) V {\displaystyle
{\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac
{QK^{\mathrm {T} }}{\sqrt {d_{k}}}}+sB\right)V\end{aligned}}}
![{\\displaystyle
{\\begin{aligned}{\\text{Attention}}\(Q,K,V\)={\\text{softmax}}\\left\({\\frac
{QK^{\\mathrm {T} }}{\\sqrt
{d_{k}}}}+sB\\right\)V\\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/bffa099b8703700a9c48178b2158edb858fc58b9)Here,
s {\displaystyle s} ![{\\displaystyle
s}](https://wikimedia.org/api/rest_v1/media/math/render/svg/01d131dfd7673938b947072a13a9744fe997e632)
is a real number ("scalar"), and  B {\displaystyle B} ![{\\displaystyle
B}](https://wikimedia.org/api/rest_v1/media/math/render/svg/47136aad860d145f75f3eed3022df827cee94d7a)
is the _linear bias_ matrix defined by B = ( 0 1 2 3 ⋯ − 1 0 1 2 ⋯ − 2 − 1 0 1
⋯ − 3 − 2 − 1 0 ⋯ ⋮ ⋮ ⋮ ⋮ ⋱ ) {\displaystyle B={\begin{pmatrix}0&1&2&3&\cdots
\\\\-1&0&1&2&\cdots \\\\-2&-1&0&1&\cdots \\\\-3&-2&-1&0&\cdots \\\\\vdots
&\vdots &\vdots &\vdots &\ddots \\\\\end{pmatrix}}} ![{\\displaystyle
B={\\begin{pmatrix}0&1&2&3&\\cdots \\\\-1&0&1&2&\\cdots \\\\-2&-1&0&1&\\cdots
\\\\-3&-2&-1&0&\\cdots \\\\\\vdots &\\vdots &\\vdots &\\vdots &\\ddots
\\\\\\end{pmatrix}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/12fa6edca20501fef7d70c74860db1e2fc70068a)in
other words,  B i , j = j − i {\displaystyle B_{i,j}=j-i} ![{\\displaystyle
B_{i,j}=j-i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/1be4dbbb894617d7ae4dd3118e0be60cd018aec7).
The idea being that the linear bias matrix is a softened mask. Just as  0
{\displaystyle 0} ![{\\displaystyle
0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2aae8864a3c1fec9585261791a809ddec1489950)
represent full attention paid, and  − ∞ {\displaystyle -\infty }
![{\\displaystyle -\\infty
}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ca2608c4b5fd3bffc73585f8c67e379b4e99b6f1)
represents no attention paid, the linear bias matrix increases attention paid
in one direction and decreases attention paid in the other direction.

ALiBi allows pretraining on short context windows, then fine-tuning on longer
context windows. Since it is directly plugged into the attention mechanism, it
can be combined with any positional encoder that is plugged into the "bottom"
of the entire network (which is where the sinusoidal encoder on the original
transformer, as well as RoPE and many others, are located).

#### Relative Position Encodings

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=34
"Edit section: Relative Position Encodings")]

Relative Position Encodings[72] is similar to ALiBi, but more generic:
Attention ( Q , K , V ) = softmax ( Q K T d k + B ) V {\displaystyle
{\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac
{QK^{\mathrm {T} }}{\sqrt {d_{k}}}}+B\right)V\end{aligned}}} ![{\\displaystyle
{\\begin{aligned}{\\text{Attention}}\(Q,K,V\)={\\text{softmax}}\\left\({\\frac
{QK^{\\mathrm {T} }}{\\sqrt
{d_{k}}}}+B\\right\)V\\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f15684ca2a0019fc697c04d62cea397b8f47dbb2)where
B {\displaystyle B} ![{\\displaystyle
B}](https://wikimedia.org/api/rest_v1/media/math/render/svg/47136aad860d145f75f3eed3022df827cee94d7a)
is a [Toeplitz matrix](/wiki/Toeplitz_matrix "Toeplitz matrix"), that is,  B i
, j = B i ′ , j ′ {\displaystyle B_{i,j}=B_{i',j'}} ![{\\displaystyle
B_{i,j}=B_{i',j'}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fe7155b71c5f6c6f726c49a3c7f3a9047414171d)
whenever  i − j = i ′ − j ′ {\displaystyle i-j=i'-j'} ![{\\displaystyle
i-j=i'-j'}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a421740142156ea5322442d9d58cf47412bd30bf).
This is contrasted with the original sinusoidal positional encoding, which is
an "absolute positional encoding".[73]

### Efficient implementation

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=35
"Edit section: Efficient implementation")]

The transformer model has been implemented in standard deep learning
[frameworks](/wiki/Framework_\(computer_science\) "Framework \(computer
science\)") such as [TensorFlow](/wiki/TensorFlow "TensorFlow") and
[PyTorch](/wiki/PyTorch "PyTorch"). _Transformers_ is a library produced by
[Hugging Face](/wiki/Hugging_Face "Hugging Face") that supplies transformer-
based architectures and pretrained models.[11]

#### KV caching

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=36
"Edit section: KV caching")]

When an autoregressive transformer is used for inference, such as generating
text, the query vector is different at each step, but the already-computed key
and value vectors are always the same. The **KV caching** method saves the
computed key and value vectors at each attention block, so that they are not
recomputed at each new token. **PagedAttention** applies [memory
paging](/wiki/Memory_paging "Memory paging") to KV caching.[74][75][76]

If a transformer is used with a baked-in prompt, such as ["You are a customer
support agent..."], then the key and value vectors can be computed for the
prompt, and saved on disk. The saving in compute is significant when the model
is used for many short real-time interactions, such as in online chatbots.

#### FlashAttention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=37
"Edit section: FlashAttention")]

FlashAttention[77] is an algorithm that implements the transformer attention
mechanism efficiently on a [GPU](/wiki/Graphics_processing_unit "Graphics
processing unit"). It is a communication-avoiding algorithm that performs
[matrix multiplications in blocks](/wiki/Block_matrix#Block_matrix_operations
"Block matrix"), such that each block fits within the
[cache](/wiki/Cache_\(computing\) "Cache \(computing\)") of a GPU, and by
careful management of the blocks it minimizes data copying between GPU caches
(as data movement is slow). See the page on
[softmax](/wiki/Softmax_function#Numerical_algorithms "Softmax function") for
details.

An improved version, FlashAttention-2,[78][79][80] was developed to cater to
the rising demand for language models capable of handling longer context
lengths. It offers enhancements in work partitioning and parallelism, enabling
it to achieve up to 230 TFLOPs/s on [A100](/wiki/Nvidia_A100 "Nvidia A100")
GPUs ([FP16](/wiki/FP16 "FP16")/[BF16](/wiki/BF16 "BF16")), a 2x speed
increase over the original FlashAttention.

Key advancements in FlashAttention-2 include the reduction of non-matmul
FLOPs, improved parallelism over the sequence length dimension, better work
partitioning between GPU warps, and added support for head dimensions up to
256 and multi-query attention (MQA) and grouped-query attention (GQA).[81]

Benchmarks revealed FlashAttention-2 to be up to 2x faster than FlashAttention
and up to 9x faster than a standard attention implementation in PyTorch.
Future developments include optimization for new hardware like
[H100](/wiki/Nvidia_H100 "Nvidia H100") GPUs and new data types like
[FP8](/wiki/Floating-point_arithmetic "Floating-point arithmetic").

FlashAttention-4 focuses on [pipelining](/wiki/Pipeline_\(Unix\) "Pipeline
\(Unix\)") to increase instruction [throughput](/wiki/Network_throughput
"Network throughput"), and was developed to perform particularly well on
[Blackwell GPUs](/wiki/Blackwell_\(microarchitecture\) "Blackwell
\(microarchitecture\)").[82]

#### Multi-Query Attention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=38
"Edit section: Multi-Query Attention")]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/8/83/DeepSeek_KV_cache_comparison_between_MHA%2C_GQA%2C_MQA%2C_MLA.svg/250px-
DeepSeek_KV_cache_comparison_between_MHA%2C_GQA%2C_MQA%2C_MLA.svg.png)](/wiki/File:DeepSeek_KV_cache_comparison_between_MHA,_GQA,_MQA,_MLA.svg)Comparison
between several different forms of attention mechanism and the amount of KV
caching necessary for each

Multi-Query Attention changes the Multihead Attention mechanism.[83] Whereas
normally,

MultiheadAttention ( Q , K , V ) = Concat i ∈ [ n heads ] ( Attention ( X W i
Q , X W i K , X W i V ) ) W O {\displaystyle
{\text{MultiheadAttention}}(Q,K,V)={\text{Concat}}_{i\in
[n_{\text{heads}}]}\left({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V})\right)W^{O}}
![{\\displaystyle
{\\text{MultiheadAttention}}\(Q,K,V\)={\\text{Concat}}_{i\\in
\[n_{\\text{heads}}\]}\\left\({\\text{Attention}}\(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}\)\\right\)W^{O}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/02afa45e87322c7c0b4919c8ba934861b54fc06e)with
Multi-Query Attention, there is just one  W K , W V {\displaystyle
W^{K},W^{V}} ![{\\displaystyle
W^{K},W^{V}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d4e0456602ee9f229ab1286d5f486eb5f71332ae),
thus:

MultiQueryAttention ( Q , K , V ) = Concat i ∈ [ n heads ] ( Attention ( X W i
Q , X W K , X W V ) ) W O {\displaystyle
{\text{MultiQueryAttention}}(Q,K,V)={\text{Concat}}_{i\in
[n_{\text{heads}}]}\left({\text{Attention}}(XW_{i}^{Q},XW^{K},XW^{V})\right)W^{O}}
![{\\displaystyle
{\\text{MultiQueryAttention}}\(Q,K,V\)={\\text{Concat}}_{i\\in
\[n_{\\text{heads}}\]}\\left\({\\text{Attention}}\(XW_{i}^{Q},XW^{K},XW^{V}\)\\right\)W^{O}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2eb0939568b3364f0c300eca805463355ce6d554)

This has a neutral effect on model quality and training speed, but increases
inference speed.

More generally, grouped-query attention (GQA) partitions attention heads into
groups, each of which shares the key-value pair. MQA is GQA with one group,
while standard Multihead Attention is GQA with the maximal number of
groups.[84]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/2/20/DeepSeek_MoE_and_MLA_%28DeepSeek-V2%29.svg/250px-
DeepSeek_MoE_and_MLA_%28DeepSeek-V2%29.svg.png)](/wiki/File:DeepSeek_MoE_and_MLA_\(DeepSeek-V2\).svg)The
architecture of V2, showing both MLA and a variant of [mixture of
experts](/wiki/Mixture_of_experts "Mixture of experts")[85]: Figure 2

Multihead Latent Attention (MLA) is a [low-rank approximation](/wiki/Low-
rank_approximation "Low-rank approximation") to standard MHA. Specifically,
each hidden vector, before entering the attention mechanism, is first
projected to two low-dimensional spaces ("latent space"), one for query and
one for key-value (KV vector). This design minimizes the KV cache, as only the
low-dimensional KV vector needs to be cached.[85]

#### Speculative decoding

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=39
"Edit section: Speculative decoding")]

Speculative decoding[86][87] is a method to accelerate token decoding.
Similarly to [speculative execution](/wiki/Speculative_execution "Speculative
execution") in CPUs, future tokens are computed quickly, then verified. If the
quickly computed tokens are incorrect, they are discarded and computed slowly.

The key factor in speculative decoding is that a transformer decoder can
verify faster than it can decode, in the following sense.

Suppose we have two transformer models like GPT-3 and GPT-3-small, both with a
context window size of 512. To generate an entire context window
autoregressively with greedy decoding with GPT-3, it must be run for 512
times, each time generating a token  x 1 , x 2 , . . . , x 512 {\displaystyle
x_{1},x_{2},...,x_{512}} ![{\\displaystyle
x_{1},x_{2},...,x_{512}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fd0b4677bb81d2d8af40d42edf0c42d0b2eaa34e),
taking time  512 T GPT-3 {\displaystyle 512T_{\text{GPT-3}}} ![{\\displaystyle
512T_{\\text{GPT-3}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/68cfccf622ab2cc50786ad9bcdc7ed5ab1dff812).
However, if we had some educated guess for the values of these tokens, we
could verify all of them in parallel, in one run of the model, by checking
that each  x t {\displaystyle x_{t}} ![{\\displaystyle
x_{t}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f279a30bc8eabc788f3fe81c9cfb674e72e858db)
is indeed the token with the largest log-likelihood in the  t {\displaystyle
t} ![{\\displaystyle
t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560)-th
output.

In speculative decoding, a smaller model or some other simple heuristic is
used to generate a few speculative tokens that are subsequently verified by
the larger model. For example, suppose we use GPT-3-small to generate four
speculative tokens:  x ~ 1 , x ~ 2 , x ~ 3 , x ~ 4 {\displaystyle {\tilde
{x}}_{1},{\tilde {x}}_{2},{\tilde {x}}_{3},{\tilde {x}}_{4}} ![{\\displaystyle
{\\tilde {x}}_{1},{\\tilde {x}}_{2},{\\tilde {x}}_{3},{\\tilde
{x}}_{4}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d8db060dad8f25abc632d0c847694d10943fefc0).
This only takes  4 T GPT-3-small {\displaystyle 4T_{\text{GPT-3-small}}}
![{\\displaystyle
4T_{\\text{GPT-3-small}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f27766b2e3974a6b36c1a34989690d453598eedd).
These tokens are then run through the larger GPT-3 in one go. Suppose that  x
~ 1 {\displaystyle {\tilde {x}}_{1}} ![{\\displaystyle {\\tilde
{x}}_{1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/bd6433a2811e7287025f60332718fe31d72003a7)
and  x ~ 2 {\displaystyle {\tilde {x}}_{2}} ![{\\displaystyle {\\tilde
{x}}_{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e6c8b294488a1ddcc0380c8a8cb75b3410fe7ede)
are verified by GPT-3 as what it would have picked, then those are kept, but
x ~ 3 {\displaystyle {\tilde {x}}_{3}} ![{\\displaystyle {\\tilde
{x}}_{3}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2de3175aa437329b2c5b3a3fc1167be15882b81d)
is not, so  x ~ 3 , x ~ 4 {\displaystyle {\tilde {x}}_{3},{\tilde {x}}_{4}}
![{\\displaystyle {\\tilde {x}}_{3},{\\tilde
{x}}_{4}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fa75c04dd4b830a3f8686e81cc88136365640db8)
are discarded, and GPT-3 is run on those. This would take  4 T GPT-3-small + 3
T GPT-3 {\displaystyle 4T_{\text{GPT-3-small}}+3T_{\text{GPT-3}}}
![{\\displaystyle
4T_{\\text{GPT-3-small}}+3T_{\\text{GPT-3}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4c60c2a824e236297f444a500e8c324540dfd24d),
which might be shorter than  4 T GPT-3 {\displaystyle 4T_{\text{GPT-3}}}
![{\\displaystyle
4T_{\\text{GPT-3}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e2bf07e1b17f4de6fb7480487563b3a31613dfd7).

For non-greedy decoding, similar ideas apply, except the speculative tokens
are accepted or rejected stochastically, in a way that guarantees the final
output distribution is the same as if speculative decoding was not
used.[86][88]

[![](//upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Multi-
Token_Prediction_%28DeepSeek%29_01.svg/250px-Multi-
Token_Prediction_%28DeepSeek%29_01.svg.png)](/wiki/File:Multi-
Token_Prediction_\(DeepSeek\)_01.svg)Multi-token prediction

In Multi-Token Prediction, a single forward pass creates a final embedding
vector, which then is un-embedded into a token probability. However, that
vector can then be further processed by another transformer block to predict
the _next_ token, and so on for arbitrarily many steps into the future. This
trades off accuracy for speed, since each new token costs just one more
transformer block, rather than the entire stack.[89][90]

### Sub-quadratic transformers

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=40
"Edit section: Sub-quadratic transformers")]

Training transformer-based architectures can be expensive, especially for long
inputs.[91] Many methods have been developed to attempt to address the issue.
In the image domain, Swin transformer is an efficient architecture that
performs attention inside shifting windows.[92] In the audio domain, SepTr
decouples the attention in time and frequency domains.[93] _Long Range Arena_
(2020)[94] is a standard benchmark for comparing the behavior of transformer
architectures over long inputs.

#### Alternative attention graphs

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=41
"Edit section: Alternative attention graphs")]

The standard attention graph is either all-to-all or causal, both of which
scales as  O ( N 2 ) {\displaystyle O(N^{2})} ![{\\displaystyle
O\(N^{2}\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e5d43a3df904fa4d7220f5b86285298aa36d969b)
where  N {\displaystyle N} ![{\\displaystyle
N}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5e3890c981ae85503089652feb48b191b57aae3)
is the number of tokens in a sequence.

Reformer (2020)[91][95] reduces the computational load from  O ( N 2 )
{\displaystyle O(N^{2})} ![{\\displaystyle
O\(N^{2}\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e5d43a3df904fa4d7220f5b86285298aa36d969b)
to  O ( N ln ⁡ N ) {\displaystyle O(N\ln N)} ![{\\displaystyle O\(N\\ln
N\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d3d19d1f2923ba0d7170ade3df165c0de1d2423e)
by using [locality-sensitive hashing](/wiki/Locality-sensitive_hashing
"Locality-sensitive hashing") and reversible layers.[96]

Sparse attention[97] uses attention graphs that grows slower than  O ( N 2 )
{\displaystyle O(N^{2})} ![{\\displaystyle
O\(N^{2}\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e5d43a3df904fa4d7220f5b86285298aa36d969b).
For example, BigBird (2020)[98] uses random [small-world
networks](/wiki/Small-world_network "Small-world network") which grows as  O (
N ) {\displaystyle O(N)} ![{\\displaystyle
O\(N\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/78484c5c26cfc97bb3b915418caa09454421e80b).

Ordinary transformers require a memory size that is quadratic in the size of
the context window. Attention-free transformers[99] reduce this to a linear
dependence while still retaining the advantages of a transformer by linking
the key to the value.

#### Random Feature Attention

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=42
"Edit section: Random Feature Attention")]

Random Feature Attention (2021)[100] uses [Fourier random
features](/wiki/Radial_basis_function_kernel#Fourier_random_features "Radial
basis function kernel"): φ ( x ) = 1 D [ cos ⁡ ⟨ w 1 , x ⟩ , sin ⁡ ⟨ w 1 , x ⟩
, ⋯ cos ⁡ ⟨ w D , x ⟩ , sin ⁡ ⟨ w D , x ⟩ ] T {\displaystyle \varphi
(x)={\frac {1}{\sqrt {D}}}[\cos \langle w_{1},x\rangle ,\sin \langle
w_{1},x\rangle ,\cdots \cos \langle w_{D},x\rangle ,\sin \langle
w_{D},x\rangle ]^{T}} ![{\\displaystyle \\varphi \(x\)={\\frac {1}{\\sqrt
{D}}}\[\\cos \\langle w_{1},x\\rangle ,\\sin \\langle w_{1},x\\rangle ,\\cdots
\\cos \\langle w_{D},x\\rangle ,\\sin \\langle w_{D},x\\rangle
\]^{T}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/243ed0310c01dc8193d985ea838e92191cec4fac)where
w 1 , . . . , w D {\displaystyle w_{1},...,w_{D}} ![{\\displaystyle
w_{1},...,w_{D}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c97fcd8d8f90947efda4e03b5ffc293c61cb094c)
are independent samples from the normal distribution  N ( 0 , σ 2 I )
{\displaystyle N(0,\sigma ^{2}I)} ![{\\displaystyle N\(0,\\sigma
^{2}I\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9d30d920f052b8230e76c64a55f2cddc963b201f).
This choice of parameters satisfy  E [ ⟨ φ ( x ) , φ ( y ) ⟩ ] = e − ‖ x − y ‖
2 2 σ 2 {\displaystyle \mathbb {E} [\langle \varphi (x),\varphi (y)\rangle
]=e^{-{\frac {\|x-y\|^{2}}{2\sigma ^{2}}}}} ![{\\displaystyle \\mathbb {E}
\[\\langle \\varphi \(x\),\\varphi \(y\)\\rangle \]=e^{-{\\frac
{\\|x-y\\|^{2}}{2\\sigma
^{2}}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2e0f85eabd1581c50b848cf5d2d73ce4e7ac6e1d),
or  e ⟨ x , y ⟩ / σ 2 = E [ ⟨ e ‖ x ‖ 2 / 2 σ 2 φ ( x ) , e ‖ y ‖ 2 / 2 σ 2 φ
( y ) ⟩ ] ≈ ⟨ e ‖ x ‖ 2 / 2 σ 2 φ ( x ) , e ‖ y ‖ 2 / 2 σ 2 φ ( y ) ⟩
{\displaystyle e^{\langle x,y\rangle /\sigma ^{2}}=\mathbb {E} [\langle
e^{\|x\|^{2}/2\sigma ^{2}}\varphi (x),e^{\|y\|^{2}/2\sigma ^{2}}\varphi
(y)\rangle ]\approx \langle e^{\|x\|^{2}/2\sigma ^{2}}\varphi
(x),e^{\|y\|^{2}/2\sigma ^{2}}\varphi (y)\rangle } ![{\\displaystyle
e^{\\langle x,y\\rangle /\\sigma ^{2}}=\\mathbb {E} \[\\langle
e^{\\|x\\|^{2}/2\\sigma ^{2}}\\varphi \(x\),e^{\\|y\\|^{2}/2\\sigma
^{2}}\\varphi \(y\)\\rangle \]\\approx \\langle e^{\\|x\\|^{2}/2\\sigma
^{2}}\\varphi \(x\),e^{\\|y\\|^{2}/2\\sigma ^{2}}\\varphi \(y\)\\rangle
}](https://wikimedia.org/api/rest_v1/media/math/render/svg/bfb56111453c9e03415021c39d21ed88a37d2ea1)Consequently,
the one-headed attention, with one query, can be written as  Attention ( q , K
, V ) = softmax ( q K T d k ) V ≈ φ ( q ) T ∑ i e ‖ k i ‖ 2 / 2 σ 2 φ ( k i )
v i T φ ( q ) T ∑ i e ‖ k i ‖ 2 / 2 σ 2 φ ( k i ) {\displaystyle
{\text{Attention}}(q,K,V)={\text{softmax}}\left({\frac {qK^{\mathrm {T}
}}{\sqrt {d_{k}}}}\right)V\approx {\frac {\varphi (q)^{T}\sum
_{i}e^{\|k_{i}\|^{2}/2\sigma ^{2}}\varphi (k_{i})v_{i}^{T}}{\varphi
(q)^{T}\sum _{i}e^{\|k_{i}\|^{2}/2\sigma ^{2}}\varphi (k_{i})}}}
![{\\displaystyle
{\\text{Attention}}\(q,K,V\)={\\text{softmax}}\\left\({\\frac {qK^{\\mathrm
{T} }}{\\sqrt {d_{k}}}}\\right\)V\\approx {\\frac {\\varphi \(q\)^{T}\\sum
_{i}e^{\\|k_{i}\\|^{2}/2\\sigma ^{2}}\\varphi \(k_{i}\)v_{i}^{T}}{\\varphi
\(q\)^{T}\\sum _{i}e^{\\|k_{i}\\|^{2}/2\\sigma ^{2}}\\varphi
\(k_{i}\)}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/bca1667ac7c453bd1979496b1b951fc9c09d3b08)where
σ = d K 1 / 4 {\displaystyle \sigma =d_{K}^{1/4}} ![{\\displaystyle \\sigma
=d_{K}^{1/4}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d2571d23e3b9162609ece1399f4abf50811e4eb6).
Similarly for multiple queries, and for multihead attention.

This approximation can be computed in linear time, as we can compute the
matrix  φ ( k i ) v i T {\displaystyle \varphi (k_{i})v_{i}^{T}}
![{\\displaystyle \\varphi
\(k_{i}\)v_{i}^{T}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6276b79cd088813503ec00ae5eab91ab02d8a7f0)
first, then multiply it with the query. In essence, we have managed to obtain
a more precise version of  Attention ( Q , K , V ) = softmax ( Q K T d k ) V ≈
Q ( K T V / d k ) {\displaystyle
{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T}
}}{\sqrt {d_{k}}}}\right)V\approx Q(K^{T}V/{\sqrt {d_{k}}})} ![{\\displaystyle
{\\text{Attention}}\(Q,K,V\)={\\text{softmax}}\\left\({\\frac {QK^{\\mathrm
{T} }}{\\sqrt {d_{k}}}}\\right\)V\\approx Q\(K^{T}V/{\\sqrt
{d_{k}}}\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7da7e0c09e0f526924af6c95f7c0d2c6fb34b910)Performer
(2022)[101] uses the same Random Feature Attention, but  w 1 , . . . , w D
{\displaystyle w_{1},...,w_{D}} ![{\\displaystyle
w_{1},...,w_{D}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c97fcd8d8f90947efda4e03b5ffc293c61cb094c)
are first independently sampled from the normal distribution  N ( 0 , σ 2 I )
{\displaystyle N(0,\sigma ^{2}I)} ![{\\displaystyle N\(0,\\sigma
^{2}I\)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9d30d920f052b8230e76c64a55f2cddc963b201f),
then they are [Gram-Schmidt processed](/wiki/Gram%E2%80%93Schmidt_process
"Gram–Schmidt process").

### Multimodality

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=43
"Edit section: Multimodality")]

Transformers can also be used/adapted for modalities (input or output) beyond
just text, usually by finding a way to "tokenize" the modality.

Multimodal models can either be trained from scratch, or by finetuning. A 2022
study found that transformers pretrained only on natural language can be
finetuned on only 0.03% of parameters and become competitive with
[LSTMs](/wiki/LSTMs "LSTMs") on a variety of logical and visual tasks,
demonstrating [transfer learning](/wiki/Transfer_learning "Transfer
learning").[102] The LLaVA was a vision-language model composed of a language
model (Vicuna-13B)[103] and a vision model ([ViT](/wiki/Vision_transformer
"Vision transformer")-L/14), connected by a linear layer. Only the linear
layer is finetuned.[104]

[Vision transformers](/wiki/Vision_transformer "Vision transformer")[41] adapt
the transformer to computer vision by breaking down input images as a series
of patches, turning them into vectors, and treating them like embedding vector
of tokens in a standard transformer.

Conformer[42] and later [Whisper](/wiki/Whisper_\(speech_recognition_system\)
"Whisper \(speech recognition system\)")[105] follow the same pattern for
[speech recognition](/wiki/Speech_recognition "Speech recognition"), first
turning the speech signal into a [spectrogram](/wiki/Spectrogram
"Spectrogram"), which is then treated like an image, i.e. broken down into a
series of patches, turned into vectors and treated like embedding vector of
tokens in a standard transformer.

[Perceivers](/wiki/Perceiver "Perceiver")[106][107] are a variant of
transformers designed for multimodality.

For image generation, notable architectures are [DALL-E 1](/wiki/DALL-E
"DALL-E") (2021), Parti (2022),[108] Phenaki (2023),[109] and Muse
(2023).[110] Unlike later models, DALL-E is not a [diffusion
model](/wiki/Diffusion_model "Diffusion model"). Instead, it uses a decoder-
only transformer that autoregressively generates a text, followed by the token
representation of an image, which is then converted by a [variational
autoencoder](/wiki/Variational_autoencoder "Variational autoencoder") to an
image.[111] Parti is an encoder–decoder transformer, where the encoder
processes a text prompt, and the decoder generates a token representation of
an image.[112] Muse is an encoder-only transformer that is trained to predict
masked image tokens from unmasked image tokens. During generation, all input
tokens are masked, and the highest-confidence predictions are included for the
next iteration, until all tokens are predicted.[110] Phenaki is a text-to-
video model. It is a bidirectional masked transformer conditioned on pre-
computed text tokens. The generated tokens are then decoded to a video.[109]

## Applications

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=44
"Edit section: Applications")]

The transformer has had great success in [natural language
processing](/wiki/Natural_language_processing "Natural language processing")
(NLP). Many [large language models](/wiki/Large_language_model "Large language
model") such as [GPT-2](/wiki/GPT-2 "GPT-2"), [GPT-3](/wiki/GPT-3 "GPT-3"),
[GPT-4](/wiki/GPT-4 "GPT-4"), [Gemini](/wiki/Gemini_\(chatbot\) "Gemini
\(chatbot\)"), AlbertAGPT, [Claude](/wiki/Anthropic#Claude "Anthropic"),
[BERT](/wiki/BERT_\(language_model\) "BERT \(language model\)"),
[Grok](/wiki/Grok_\(chatbot\) "Grok \(chatbot\)"), [XLNet](/wiki/XLNet
"XLNet"), [RoBERTa](/wiki/BERT_\(language_model\)#RoBERTa "BERT \(language
model\)") and [ChatGPT](/wiki/ChatGPT "ChatGPT") demonstrate the ability of
transformers to perform a wide variety of NLP-related subtasks and their
related real-world applications, including:

  * [machine translation](/wiki/Machine_translation "Machine translation")
  * [time series](/wiki/Time_series "Time series") prediction
  * [document summarization](/wiki/Automatic_summarization "Automatic summarization")
  * [document generation](/wiki/Natural_language_generation "Natural language generation")
  * [named entity recognition](/wiki/Named-entity_recognition "Named-entity recognition") (NER)[113]
  * [writing computer code](/wiki/Computer_programming "Computer programming") based on requirements expressed in natural language.
  * [speech-to-text](/wiki/Speech-to-text "Speech-to-text")

Beyond traditional NLP, the transformer architecture has had success in other
applications, such as:

  * [biological sequence analysis](/wiki/Sequence_analysis "Sequence analysis")
  * [video understanding](/wiki/Computer_vision "Computer vision")
  * [protein folding](/wiki/Protein_structure_prediction "Protein structure prediction") (such as [AlphaFold](/wiki/AlphaFold "AlphaFold"))
  * [evaluating](/wiki/Evaluation_function "Evaluation function") chess board positions. Using static evaluation alone (that is, with no [Minimax](/wiki/Minimax "Minimax") search) transformer achieved an [Elo](/wiki/Elo_rating_system "Elo rating system") of 2895, putting it at [grandmaster](/wiki/Grandmaster_\(chess\) "Grandmaster \(chess\)") level.[10]

## See also

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=45
"Edit section: See also")]

  * [seq2seq](/wiki/Seq2seq "Seq2seq") – Family of machine learning approaches
  * [Perceiver](/wiki/Perceiver "Perceiver") – Variant of Transformer designed for multimodal data
  * [Vision transformer](/wiki/Vision_transformer "Vision transformer") – Machine learning model for vision processing
  * [Large language model](/wiki/Large_language_model "Large language model") – Type of machine learning model
  * [BERT (language model)](/wiki/BERT_\(language_model\) "BERT \(language model\)") – Series of language models developed by Google AI
  * [Generative pre-trained transformer](/wiki/Generative_pre-trained_transformer "Generative pre-trained transformer") – Type of large language model
  * [T5 (language model)](/wiki/T5_\(language_model\) "T5 \(language model\)") – Series of large language models developed by Google AI

## Notes

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=46
"Edit section: Notes")]

  1. **^** [Gated recurrent units](/wiki/Gated_recurrent_units "Gated recurrent units") (2014) further reduced its complexity.
  2. **^** Some architectures, such as RWKV or state space models, avoid the issue.

## References

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=47
"Edit section: References")]

  1. ^ _**a**_ _**b**_ _**c**_ _**d**_ _**e**_ _**f**_ _**g**_ _**h**_ _**i**_ _**j**_ _**k**_ _**l**_ [Vaswani, Ashish](/wiki/Ashish_Vaswani "Ashish Vaswani"); Shazeer, Noam; Parmar, Niki; Uszkoreit, Jakob; Jones, Llion; [Gomez, Aidan N](/wiki/Aidan_Gomez "Aidan Gomez"); Kaiser, Łukasz; Polosukhin, Illia (2017). ["Attention is All you Need"](https://proceedings.neurips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf) (PDF). _Advances in Neural Information Processing Systems_. **30**. Curran Associates, Inc.
  2. **^** [Hochreiter, Sepp](/wiki/Sepp_Hochreiter "Sepp Hochreiter"); [Schmidhuber, Jürgen](/wiki/J%C3%BCrgen_Schmidhuber "Jürgen Schmidhuber") (1 November 1997). "Long Short-Term Memory". _Neural Computation_. **9** (8): 1735–1780\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1162/neco.1997.9.8.1735](https://doi.org/10.1162%2Fneco.1997.9.8.1735). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [0899-7667](https://search.worldcat.org/issn/0899-7667). [PMID](/wiki/PMID_\(identifier\) "PMID \(identifier\)") [9377276](https://pubmed.ncbi.nlm.nih.gov/9377276). [S2CID](/wiki/S2CID_\(identifier\) "S2CID \(identifier\)") [1915014](https://api.semanticscholar.org/CorpusID:1915014).
  3. ^ _**a**_ _**b**_ ["Better Language Models and Their Implications"](https://openai.com/blog/better-language-models/). _OpenAI_. 2019-02-14. [Archived](https://web.archive.org/web/20201219132206/https://openai.com/blog/better-language-models/) from the original on 2020-12-19. Retrieved 2019-08-25.
  4. ^ _**a**_ _**b**_ Bahdanau; Cho, Kyunghyun; Bengio, Yoshua (September 1, 2014). "Neural Machine Translation by Jointly Learning to Align and Translate". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1409.0473](https://arxiv.org/abs/1409.0473) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  5. **^** Luong, Minh-Thang; Pham, Hieu; Manning, Christopher D. (August 17, 2015). "Effective Approaches to Attention-based Neural Machine Translation". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1508.04025](https://arxiv.org/abs/1508.04025) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  6. ^ _**a**_ _**b**_ Chen, Lili; Lu, Kevin; Rajeswaran, Aravind; Lee, Kimin; Grover, Aditya; Laskin, Michael; Abbeel, Pieter; Srinivas, Aravind; Mordatch, Igor (2021-06-24), _Decision Transformer: Reinforcement Learning via Sequence Modeling_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2106.01345](https://arxiv.org/abs/2106.01345)
  7. **^** Parisotto, Emilio; Song, Francis; Rae, Jack; Pascanu, Razvan; Gulcehre, Caglar; Jayakumar, Siddhant; Jaderberg, Max; Kaufman, Raphaël Lopez; Clark, Aidan; Noury, Seb; Botvinick, Matthew; Heess, Nicolas; Hadsell, Raia (2020-11-21). ["Stabilizing Transformers for Reinforcement Learning"](https://proceedings.mlr.press/v119/parisotto20a.html). _Proceedings of the 37th International Conference on Machine Learning_. PMLR: 7487–7498.
  8. **^** Radford, Alec; Jong Wook Kim; Xu, Tao; Brockman, Greg; McLeavey, Christine; Sutskever, Ilya (2022). "Robust Speech Recognition via Large-Scale Weak Supervision". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2212.04356](https://arxiv.org/abs/2212.04356) [[eess.AS](https://arxiv.org/archive/eess.AS)].
  9. **^** Monastirsky, Maxim; Azulay, Osher; Sintov, Avishai (February 2023). "Learning to Throw With a Handful of Samples Using Decision Transformers". _IEEE Robotics and Automation Letters_. **8** (2): 576–583\. [Bibcode](/wiki/Bibcode_\(identifier\) "Bibcode \(identifier\)"):[2023IRAL....8..576M](https://ui.adsabs.harvard.edu/abs/2023IRAL....8..576M). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1109/LRA.2022.3229266](https://doi.org/10.1109%2FLRA.2022.3229266). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [2377-3766](https://search.worldcat.org/issn/2377-3766).
  10. ^ _**a**_ _**b**_ Ruoss, Anian; Delétang, Grégoire; Medapati, Sourabh; Grau-Moya, Jordi; Wenliang, Li; Catt, Elliot; Reid, John; Genewein, Tim (2024-02-07). "Grandmaster-Level Chess Without Search". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2402.04494v1](https://arxiv.org/abs/2402.04494v1) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  11. ^ _**a**_ _**b**_ Wolf, Thomas; Debut, Lysandre; Sanh, Victor; Chaumond, Julien; Delangue, Clement; Moi, Anthony; Cistac, Pierric; Rault, Tim; Louf, Remi; Funtowicz, Morgan; Davison, Joe; Shleifer, Sam; von Platen, Patrick; Ma, Clara; Jernite, Yacine; Plu, Julien; Xu, Canwen; Le Scao, Teven; Gugger, Sylvain; Drame, Mariama; Lhoest, Quentin; Rush, Alexander (2020). "Transformers: State-of-the-Art Natural Language Processing". _Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations_. pp. 38–45\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.18653/v1/2020.emnlp-demos.6](https://doi.org/10.18653%2Fv1%2F2020.emnlp-demos.6). [S2CID](/wiki/S2CID_\(identifier\) "S2CID \(identifier\)") [208117506](https://api.semanticscholar.org/CorpusID:208117506).
  12. ^ _**a**_ _**b**_ _**c**_ ["Open Sourcing BERT: State-of-the-Art Pre-training for Natural Language Processing"](http://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html). _Google AI Blog_. 2 November 2018. [Archived](https://web.archive.org/web/20210113211449/https://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html) from the original on 2021-01-13. Retrieved 2019-08-25.
  13. **^** Feldman, J. A.; Ballard, D. H. (1982-07-01). ["Connectionist models and their properties"](https://www.sciencedirect.com/science/article/pii/S0364021382800013). _Cognitive Science_. **6** (3): 205–254\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1016/S0364-0213(82)80001-3](https://doi.org/10.1016%2FS0364-0213%2882%2980001-3). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [0364-0213](https://search.worldcat.org/issn/0364-0213).
  14. **^** Rumelhart, David E.; McClelland, James L.; Hinton, Geoffrey E. (1987-07-29). [_Parallel Distributed Processing, Volume 1: Explorations in the Microstructure of Cognition: Foundations, Chapter 2_](https://stanford.edu/~jlmcc/papers/PDP/Chapter2.pdf) (PDF). Cambridge, Mass: Bradford Books. [ISBN](/wiki/ISBN_\(identifier\) "ISBN \(identifier\)") [978-0-262-68053-0](/wiki/Special:BookSources/978-0-262-68053-0 "Special:BookSources/978-0-262-68053-0").
  15. **^** Giles, C. Lee; Maxwell, Tom (1987-12-01). ["Learning, invariance, and generalization in high-order neural networks"](https://opg.optica.org/abstract.cfm?URI=ao-26-23-4972). _Applied Optics_. **26** (23): 4972–4978\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1364/AO.26.004972](https://doi.org/10.1364%2FAO.26.004972). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [0003-6935](https://search.worldcat.org/issn/0003-6935). [PMID](/wiki/PMID_\(identifier\) "PMID \(identifier\)") [20523475](https://pubmed.ncbi.nlm.nih.gov/20523475).
  16. ^ _**a**_ _**b**_ [Schmidhuber, Jürgen](/wiki/J%C3%BCrgen_Schmidhuber "Jürgen Schmidhuber") (1992). ["Learning to control fast-weight memories: an alternative to recurrent nets"](https://archive.org/download/wikipedia-scholarly-sources-corpus/10.1162.zip/10.1162%252Fneco.1992.4.1.131.pdf) (PDF). _Neural Computation_. **4** (1): 131–139\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1162/neco.1992.4.1.131](https://doi.org/10.1162%2Fneco.1992.4.1.131). [S2CID](/wiki/S2CID_\(identifier\) "S2CID \(identifier\)") [16683347](https://api.semanticscholar.org/CorpusID:16683347).
  17. **^** Christoph von der Malsburg: The correlation theory of brain function. Internal Report 81-2, MPI Biophysical Chemistry, 1981. <http://cogprints.org/1380/1/vdM_correlation.pdf> See Reprint in Models of Neural Networks II, chapter 2, pages 95–119. Springer, Berlin, 1994.
  18. **^** Jerome A. Feldman, "Dynamic connections in neural networks," Biological Cybernetics, vol. 46, no. 1, pp. 27–39, Dec. 1982.
  19. **^** Hinton, Geoffrey E.; Plaut, David C. (1987). ["Using Fast Weights to Deblur Old Memories"](https://escholarship.org/uc/item/0570j1dp). _Proceedings of the Annual Meeting of the Cognitive Science Society_. **9**.
  20. **^** Katharopoulos, Angelos; Vyas, Apoorv; Pappas, Nikolaos; Fleuret, François (2020). ["Transformers are RNNs: Fast autoregressive Transformers with linear attention"](https://proceedings.mlr.press/v119/katharopoulos20a.html). _ICML 2020_. PMLR. pp. 5156–5165.
  21. **^** Schlag, Imanol; Irie, Kazuki; [Schmidhuber, Jürgen](/wiki/Juergen_Schmidhuber "Juergen Schmidhuber") (2021). "Linear Transformers Are Secretly Fast Weight Programmers". _ICML 2021_. Springer. pp. 9355–9366.
  22. ^ _**a**_ _**b**_ Cho, Kyunghyun; van Merriënboer, Bart; Gulcehre, Caglar; Bahdanau, Dzmitry; Bougares, Fethi; Schwenk, Holger; Bengio, Yoshua (October 2014). ["Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation"](https://aclanthology.org/D14-1179). In Moschitti, Alessandro; Pang, Bo; Daelemans, Walter (eds.). _Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)_. Doha, Qatar: Association for Computational Linguistics. pp. 1724–1734\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1406.1078](https://arxiv.org/abs/1406.1078). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.3115/v1/D14-1179](https://doi.org/10.3115%2Fv1%2FD14-1179).
  23. ^ _**a**_ _**b**_ Sutskever, Ilya; Vinyals, Oriol; Le, Quoc Viet (14 Dec 2014). "Sequence to sequence learning with neural networks". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1409.3215](https://arxiv.org/abs/1409.3215) [[cs.CL](https://arxiv.org/archive/cs.CL)]. [first version posted to arXiv on 10 Sep 2014]
  24. **^** Chung, Junyoung; Gulcehre, Caglar; Cho, KyungHyun; Bengio, Yoshua (2014). "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1412.3555](https://arxiv.org/abs/1412.3555) [[cs.NE](https://arxiv.org/archive/cs.NE)].
  25. **^** Gruber, N.; Jockisch, A. (2020), "Are GRU cells more specific and LSTM cells more sensitive in motive classification of text?", _Frontiers in Artificial Intelligence_ , **3** 40, [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.3389/frai.2020.00040](https://doi.org/10.3389%2Ffrai.2020.00040), [PMC](/wiki/PMC_\(identifier\) "PMC \(identifier\)") [7861254](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7861254), [PMID](/wiki/PMID_\(identifier\) "PMID \(identifier\)") [33733157](https://pubmed.ncbi.nlm.nih.gov/33733157), [S2CID](/wiki/S2CID_\(identifier\) "S2CID \(identifier\)") [220252321](https://api.semanticscholar.org/CorpusID:220252321)
  26. **^** Sutskever, Ilya; Vinyals, Oriol; Le, Quoc V (2014). ["Sequence to Sequence Learning with Neural Networks"](https://proceedings.neurips.cc/paper/2014/hash/a14ac55a4f27472c5d894ec1c3c743d2-Abstract.html). _Advances in Neural Information Processing Systems_. **27**. Curran Associates, Inc. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1409.3215](https://arxiv.org/abs/1409.3215).
  27. **^** Luong, Minh-Thang; Pham, Hieu; Manning, Christopher D. (2015). "Effective Approaches to Attention-based Neural Machine Translation". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1508.04025](https://arxiv.org/abs/1508.04025) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  28. **^** Wu, Yonghui; et al. (2016-09-01). "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1609.08144](https://arxiv.org/abs/1609.08144) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  29. **^** Lewis-Kraus, Gideon (2016-12-14). ["The Great A.I. Awakening"](https://web.archive.org/web/20230524052626/https://www.nytimes.com/2016/12/14/magazine/the-great-ai-awakening.html). _The New York Times_. [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [0362-4331](https://search.worldcat.org/issn/0362-4331). Archived from [the original](https://www.nytimes.com/2016/12/14/magazine/the-great-ai-awakening.html) on 24 May 2023. Retrieved 2023-06-22.
  30. **^** Parikh, Ankur P.; Täckström, Oscar; Das, Dipanjan; Uszkoreit, Jakob (2016-09-25). "A Decomposable Attention Model for Natural Language Inference". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1606.01933](https://arxiv.org/abs/1606.01933) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  31. ^ _**a**_ _**b**_ Levy, Steven. ["8 Google Employees Invented Modern AI. Here's the Inside Story"](https://www.wired.com/story/eight-google-employees-invented-modern-ai-transformers-paper/). _Wired_. [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [1059-1028](https://search.worldcat.org/issn/1059-1028). [Archived](https://web.archive.org/web/20240320101528/https://www.wired.com/story/eight-google-employees-invented-modern-ai-transformers-paper/) from the original on 20 Mar 2024. Retrieved 2024-08-06.
  32. **^** Cheng, Jianpeng; Dong, Li; Lapata, Mirella (November 2016). ["Long Short-Term Memory-Networks for Machine Reading"](https://aclanthology.org/D16-1053/). In Su, Jian; Duh, Kevin; Carreras, Xavier (eds.). _Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing_. Austin, Texas: Association for Computational Linguistics. pp. 551–561\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.18653/v1/D16-1053](https://doi.org/10.18653%2Fv1%2FD16-1053).
  33. **^** Peng, Bo; Alcaide, Eric; Anthony, Quentin; Albalak, Alon; Arcadinho, Samuel; Biderman, Stella; Cao, Huanqi; Cheng, Xin; Chung, Michael (2023-12-10), _RWKV: Reinventing RNNs for the transformer Era_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2305.13048](https://arxiv.org/abs/2305.13048)
  34. **^** Marche, Stephen (2024-08-23). ["Was Linguistic A.I. Created by Accident?"](https://www.newyorker.com/science/annals-of-artificial-intelligence/was-linguistic-ai-created-by-accident). _The New Yorker_. [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [0028-792X](https://search.worldcat.org/issn/0028-792X). Retrieved 2024-08-27.
  35. ^ _**a**_ _**b**_ _**c**_ _**d**_ _**e**_ _**f**_ Devlin, Jacob; Chang, Ming-Wei; Lee, Kenton; Toutanova, Kristina (11 October 2018). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1810.04805v2](https://arxiv.org/abs/1810.04805v2) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  36. **^** ["Google: BERT now used on almost every English query"](https://searchengineland.com/google-bert-used-on-almost-every-english-query-342193). _Search Engine Land_. 2020-10-15. Retrieved 2020-11-24.
  37. ^ _**a**_ _**b**_ Caswell, Isaac; Liang, Bowen (June 8, 2020). ["Recent Advances in Google Translate"](https://research.google/blog/recent-advances-in-google-translate/). _Google Research_. [Archived](https://web.archive.org/web/20240704042433/https://research.google/blog/recent-advances-in-google-translate/) from the original on 4 Jul 2024. Retrieved 2024-08-07.
  38. **^** ["The inside story of how ChatGPT was built from the people who made it"](https://www.technologyreview.com/2023/03/03/1069311/inside-story-oral-history-how-chatgpt-built-openai/). _MIT Technology Review_. Retrieved 2024-08-06.
  39. **^** ["Improving language understanding with unsupervised learning"](https://openai.com/research/language-unsupervised). _openai.com_. June 11, 2018. [Archived](https://web.archive.org/web/20230318210736/https://openai.com/research/language-unsupervised) from the original on 2023-03-18. Retrieved 2023-03-18.
  40. **^** [_finetune-transformer-lm_](https://github.com/openai/finetune-transformer-lm), OpenAI, June 11, 2018, retrieved 2023-05-01
  41. ^ _**a**_ _**b**_ Dosovitskiy, Alexey; Beyer, Lucas; Kolesnikov, Alexander; Weissenborn, Dirk; Zhai, Xiaohua; Unterthiner, Thomas; Dehghani, Mostafa; Minderer, Matthias; Heigold, Georg; Gelly, Sylvain; Uszkoreit, Jakob (2021-06-03). "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2010.11929](https://arxiv.org/abs/2010.11929) [[cs.CV](https://arxiv.org/archive/cs.CV)].
  42. ^ _**a**_ _**b**_ Gulati, Anmol; Qin, James; Chiu, Chung-Cheng; Parmar, Niki; Zhang, Yu; Yu, Jiahui; Han, Wei; Wang, Shibo; Zhang, Zhengdong; Wu, Yonghui; Pang, Ruoming (2020). "Conformer: Convolution-augmented Transformer for Speech Recognition". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2005.08100](https://arxiv.org/abs/2005.08100) [[eess.AS](https://arxiv.org/archive/eess.AS)].
  43. **^** Choromanski, Krzysztof; Likhosherstov, Valerii; Dohan, David; Song, Xingyou; Gane, Andreea; Sarlos, Tamas; Hawkins, Peter; Davis, Jared; Mohiuddin, Afroz (2022-11-19), _Rethinking Attention with Performers_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2009.14794](https://arxiv.org/abs/2009.14794)
  44. **^** Liu, Zhuang; Mao, Hanzi; Wu, Chao-Yuan; Feichtenhofer, Christoph; Darrell, Trevor; Xie, Saining (2022). [_A ConvNet for the 2020s_](https://openaccess.thecvf.com/content/CVPR2022/html/Liu_A_ConvNet_for_the_2020s_CVPR_2022_paper.html). Conference on Computer Vision and Pattern Recognition ([CVPR](/wiki/CVPR "CVPR")). pp. 11976–11986.
  45. **^** Esser, Patrick; Kulal, Sumith; Blattmann, Andreas; Entezari, Rahim; Müller, Jonas; Saini, Harry; Levi, Yam; Lorenz, Dominik; Sauer, Axel (2024-03-05), _Scaling Rectified Flow Transformers for High-Resolution Image Synthesis_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2403.03206](https://arxiv.org/abs/2403.03206)
  46. ^ _**a**_ _**b**_ Xiong, Ruibin; Yang, Yunchang; He, Di; Zheng, Kai; Zheng, Shuxin; Xing, Chen; Zhang, Huishuai; Lan, Yanyan; Wang, Liwei; Liu, Tie-Yan (2020-06-29). "On Layer Normalization in the Transformer Architecture". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2002.04745](https://arxiv.org/abs/2002.04745) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  47. **^** Raffel, Colin; Shazeer, Noam; Roberts, Adam; Lee, Katherine; Narang, Sharan; Matena, Michael; Zhou, Yanqi; Li, Wei; Liu, Peter J. (2020-01-01). ["Exploring the limits of transfer learning with a unified text-to-text transformer"](https://dl.acm.org/doi/abs/10.5555/3455716.3455856). _The Journal of Machine Learning Research_. **21** (1): 140:5485–140:5551. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1910.10683](https://arxiv.org/abs/1910.10683). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [1532-4435](https://search.worldcat.org/issn/1532-4435).
  48. **^** Raffel, Colin; Shazeer, Noam; Roberts, Adam; Lee, Katherine; Narang, Sharan; Matena, Michael; Zhou, Yanqi; Li, Wei; Liu, Peter J. (2019). "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1910.10683](https://arxiv.org/abs/1910.10683) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  49. ^ _**a**_ _**b**_ ["Masked language modeling"](https://huggingface.co/docs/transformers/tasks/masked_language_modeling). _huggingface.co_. Retrieved 2023-10-05.
  50. ^ _**a**_ _**b**_ ["Causal language modeling"](https://huggingface.co/docs/transformers/tasks/language_modeling). _huggingface.co_. Retrieved 2023-10-05.
  51. ^ _**a**_ _**b**_ _**c**_ _**d**_ Tay, Yi; Dehghani, Mostafa; Tran, Vinh Q.; Garcia, Xavier; Wei, Jason; Wang, Xuezhi; Chung, Hyung Won; Shakeri, Siamak; Bahri, Dara (2023-02-28), _UL2: Unifying Language Learning Paradigms_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2205.05131](https://arxiv.org/abs/2205.05131)
  52. **^** Press, Ofir; Wolf, Lior (2017-02-21), _Using the Output Embedding to Improve Language Models_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1608.05859](https://arxiv.org/abs/1608.05859)
  53. **^** Lintz, Nathan (2016-04-18). ["Sequence Modeling with Neural Networks (Part 2): Attention Models"](https://indico.io/blog/sequence-modeling-neural-networks-part2-attention-models/). _Indico_. [Archived](https://web.archive.org/web/20201021203352/https://indico.io/blog/sequence-modeling-neural-networks-part2-attention-models/) from the original on 2020-10-21. Retrieved 2019-10-15.
  54. ^ _**a**_ _**b**_ _**c**_ Alammar, Jay. ["The Illustrated transformer"](http://jalammar.github.io/illustrated-transformer/). _jalammar.github.io_. [Archived](https://web.archive.org/web/20201018061610/https://jalammar.github.io/illustrated-transformer/) from the original on 2020-10-18. Retrieved 2019-10-15.
  55. **^** Team, Keras. ["Keras documentation: GPT2Backbone model"](https://keras.io/api/keras_nlp/models/gpt2/gpt2_backbone/). _keras.io_. Retrieved 2024-08-08.
  56. **^** Clark, Kevin; Khandelwal, Urvashi; Levy, Omer; Manning, Christopher D. (August 2019). ["What Does BERT Look at? An Analysis of BERT's Attention"](https://www.aclweb.org/anthology/W19-4828). _Proceedings of the 2019 ACL Workshop BlackboxNLP: Analyzing and Interpreting Neural Networks for NLP_. Florence, Italy: Association for Computational Linguistics: 276–286\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1906.04341](https://arxiv.org/abs/1906.04341). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.18653/v1/W19-4828](https://doi.org/10.18653%2Fv1%2FW19-4828). [Archived](https://web.archive.org/web/20201021211357/https://www.aclweb.org/anthology/W19-4828/) from the original on 2020-10-21. Retrieved 2020-05-20.
  57. **^** Yang, Zhilin; Dai, Zihang; Yang, Yiming; Carbonell, Jaime; Salakhutdinov, Russ R; Le, Quoc V (2019). ["XLNet: Generalized Autoregressive Pretraining for Language Understanding"](https://proceedings.neurips.cc/paper/2019/hash/dc6a7e655d7e5840e66733e9ee67cc69-Abstract.html). _Advances in Neural Information Processing Systems_. **32**. Curran Associates, Inc. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1906.08237](https://arxiv.org/abs/1906.08237).
  58. **^** Radford, Alec; Narasimhan, Karthik; Salimans, Tim; Sutskever, Ilya (11 June 2018). ["Improving Language Understanding by Generative Pre-Training"](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) (PDF). [OpenAI](/wiki/OpenAI "OpenAI"). p. 12\. [Archived](https://web.archive.org/web/20210126024542/https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) (PDF) from the original on 26 January 2021. Retrieved 23 January 2021.
  59. **^** Wang, Qiang; Li, Bei; Xiao, Tong; Zhu, Jingbo; Li, Changliang; Wong, Derek F.; Chao, Lidia S. (2019-06-04), _Learning Deep Transformer Models for Machine Translation_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1906.01787](https://arxiv.org/abs/1906.01787)
  60. **^** Phuong, Mary; Hutter, Marcus (2022-07-19), _Formal Algorithms for Transformers_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2207.09238](https://arxiv.org/abs/2207.09238)
  61. ^ _**a**_ _**b**_ _**c**_ Raffel, Colin; Shazeer, Noam; Roberts, Adam; Lee, Katherine; Narang, Sharan; Matena, Michael; Zhou, Yanqi; Li, Wei; Liu, Peter J. (2020). ["Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer"](http://jmlr.org/papers/v21/20-074.html). _Journal of Machine Learning Research_. **21** (140): 1–67\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1910.10683](https://arxiv.org/abs/1910.10683). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [1533-7928](https://search.worldcat.org/issn/1533-7928).
  62. ^ _**a**_ _**b**_ Shazeer, Noam (2020-02-01). "GLU Variants Improve Transformer". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2002.05202](https://arxiv.org/abs/2002.05202) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  63. **^** Hendrycks, Dan; Gimpel, Kevin (2016-06-27). "Gaussian Error Linear Units (GELUs)". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1606.08415v5](https://arxiv.org/abs/1606.08415v5) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  64. **^** Zhang, Biao; Sennrich, Rico (2019). ["Root Mean Square Layer Normalization"](https://proceedings.neurips.cc/paper/2019/hash/1e8a19426224ca89e83cef47f1e7f53b-Abstract.html). _Advances in Neural Information Processing Systems_. **32**. Curran Associates, Inc. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1910.07467](https://arxiv.org/abs/1910.07467).
  65. **^** Tembine, Hamidou, Manzoor Ahmed Khan, and Issa Bamia. 2024. "Mean-Field-Type Transformers" Mathematics 12, no. 22: 3506. <https://doi.org/10.3390/math12223506>
  66. ^ _**a**_ _**b**_ Nguyen, Toan Q.; Salazar, Julian (2019-11-02). Niehues, Jan; Cattoni, Rolando; Stüker, Sebastian; Negri, Matteo; Turchi, Marco; Ha, Thanh-Le; Salesky, Elizabeth; Sanabria, Ramon; Barrault, Loic (eds.). ["Transformers without Tears: Improving the Normalization of Self-Attention"](https://aclanthology.org/2019.iwslt-1.17). _Proceedings of the 16th International Conference on Spoken Language Translation_. Hong Kong: Association for Computational Linguistics. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1910.05895](https://arxiv.org/abs/1910.05895). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.5281/zenodo.3525484](https://doi.org/10.5281%2Fzenodo.3525484).
  67. **^** Dufter, Philipp; Schmitt, Martin; Schütze, Hinrich (2022-06-06). ["Position Information in transformers: An Overview"](https://doi.org/10.1162%2Fcoli_a_00445). _Computational Linguistics_. **48** (3): 733–763\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2102.11090](https://arxiv.org/abs/2102.11090). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1162/coli_a_00445](https://doi.org/10.1162%2Fcoli_a_00445). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [0891-2017](https://search.worldcat.org/issn/0891-2017). [S2CID](/wiki/S2CID_\(identifier\) "S2CID \(identifier\)") [231986066](https://api.semanticscholar.org/CorpusID:231986066).
  68. **^** Gehring, Jonas; Auli, Michael; Grangier, David; Yarats, Denis; Dauphin, Yann N. (2017-07-17). ["Convolutional Sequence to Sequence Learning"](https://proceedings.mlr.press/v70/gehring17a.html). _Proceedings of the 34th International Conference on Machine Learning_. PMLR: 1243–1252.
  69. **^** Haviv, Adi; Ram, Ori; Press, Ofir; Izsak, Peter; Levy, Omer (2022-12-05), _Transformer Language Models without Positional Encodings Still Learn Positional Information_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2203.16634](https://arxiv.org/abs/2203.16634)
  70. **^** Su, Jianlin; Lu, Yu; Pan, Shengfeng; Murtadha, Ahmed; Wen, Bo; Liu, Yunfeng (2021-04-01). "RoFormer: Enhanced Transformer with Rotary Position Embedding". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2104.09864](https://arxiv.org/abs/2104.09864) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  71. **^** Press, Ofir; Smith, Noah A.; Lewis, Mike (2021-08-01). "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2108.12409](https://arxiv.org/abs/2108.12409) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  72. **^** Shaw, Peter; Uszkoreit, Jakob; Vaswani, Ashish (2018). "Self-Attention with Relative Position Representations". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1803.02155](https://arxiv.org/abs/1803.02155) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  73. **^** Ke, Guolin; He, Di; Liu, Tie-Yan (2021-03-15), _Rethinking Positional Encoding in Language Pre-training_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2006.15595](https://arxiv.org/abs/2006.15595)
  74. **^** Kwon, Woosuk; Li, Zhuohan; Zhuang, Siyuan; Sheng, Ying; Zheng, Lianmin; Yu, Cody Hao; Gonzalez, Joseph; Zhang, Hao; Stoica, Ion (2023-10-23). ["Efficient Memory Management for Large Language Model Serving with PagedAttention"](https://dl.acm.org/doi/10.1145/3600006.3613165). _Proceedings of the 29th Symposium on Operating Systems Principles_. SOSP '23. New York, NY, USA: Association for Computing Machinery. pp. 611–626\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2309.06180](https://arxiv.org/abs/2309.06180). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1145/3600006.3613165](https://doi.org/10.1145%2F3600006.3613165). [ISBN](/wiki/ISBN_\(identifier\) "ISBN \(identifier\)") [979-8-4007-0229-7](/wiki/Special:BookSources/979-8-4007-0229-7 "Special:BookSources/979-8-4007-0229-7").
  75. **^** [_vllm-project/vllm_](https://github.com/vllm-project/vllm), vLLM, 2024-06-20, retrieved 2024-06-20
  76. **^** Zhuohan Li, Woosuk Kwon; Zhuang, Siyuan; Sheng, Ying; Zheng, Lianmin; Yu, Cody; Gonzalez, Joey; Zhang, Hao; Stoica, Ion (2023-06-20). ["vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention"](https://blog.vllm.ai/2023/06/20/vllm.html). _vLLM Blog_. Retrieved 2024-06-20.
  77. **^** Dao, Tri; Fu, Dan; Ermon, Stefano; Rudra, Atri; Ré, Christopher (2022-12-06). ["FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html). _Advances in Neural Information Processing Systems_. **35** : 16344–16359\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2205.14135](https://arxiv.org/abs/2205.14135).
  78. **^** ["Stanford CRFM"](https://crfm.stanford.edu/2023/07/17/flash2.html). _crfm.stanford.edu_. Retrieved 2023-07-18.
  79. **^** ["FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"](https://princeton-nlp.github.io/flash-atttention-2/). _Princeton NLP_. 2023-06-17. Retrieved 2023-07-18.
  80. **^** ["Introducing Together AI Chief Scientist Tri Dao, as he releases FlashAttention-2 to speed up model training and inference"](https://together.ai/blog/tri-dao-flash-attention). _TOGETHER_. Retrieved 2023-07-18.
  81. **^** Ainslie, Joshua; Lee-Thorp, James; de Jong, Michiel; Zemlyanskiy, Yury; Lebrón, Federico; Sanghai, Sumit (2023-12-23). "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2305.13245](https://arxiv.org/abs/2305.13245) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  82. **^** ["We reverse-engineered Flash Attention 4"](https://modal.com/blog/reverse-engineer-flash-attention-4). _Modal_. Retrieved 2025-09-26.
  83. **^** Chowdhery, Aakanksha; Narang, Sharan; Devlin, Jacob; Bosma, Maarten; Mishra, Gaurav; Roberts, Adam; Barham, Paul; Chung, Hyung Won; Sutton, Charles; Gehrmann, Sebastian; Schuh, Parker; Shi, Kensen; Tsvyashchenko, Sasha; Maynez, Joshua; Rao, Abhishek (2022-04-01). "PaLM: Scaling Language Modeling with Pathways". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2204.02311](https://arxiv.org/abs/2204.02311) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  84. **^** Ainslie, Joshua; Lee-Thorp, James; de Jong, Michiel; Zemlyanskiy, Yury; Lebrón, Federico; Sanghai, Sumit (2023-12-23), _GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2305.13245](https://arxiv.org/abs/2305.13245)
  85. ^ _**a**_ _**b**_ DeepSeek-AI; Liu, Aixin; Feng, Bei; Wang, Bin; Wang, Bingxuan; Liu, Bo; Zhao, Chenggang; Dengr, Chengqi; Ruan, Chong (19 June 2024), _DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2405.04434](https://arxiv.org/abs/2405.04434).
  86. ^ _**a**_ _**b**_ Leviathan, Yaniv; Kalman, Matan; Matias, Yossi (2023-05-18), _Fast Inference from Transformers via Speculative Decoding_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2211.17192](https://arxiv.org/abs/2211.17192)
  87. **^** Fu, Yao (2023-12-13). ["Towards 100x Speedup: Full Stack Transformer Inference Optimization"](https://yaofu.notion.site/Towards-100x-Speedup-Full-Stack-Transformer-Inference-Optimization-43124c3688e14cffaf2f1d6cbdf26c6c).
  88. **^** Chen, Charlie; Borgeaud, Sebastian; Irving, Geoffrey; Lespiau, Jean-Baptiste; Sifre, Laurent; Jumper, John (2023-02-02), _Accelerating Large Language Model Decoding with Speculative Sampling_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2302.01318](https://arxiv.org/abs/2302.01318)
  89. **^** Gloeckle, Fabian; Badr Youbi Idrissi; Rozière, Baptiste; Lopez-Paz, David; Synnaeve, Gabriel (2024). "Better & Faster Large Language Models via Multi-token Prediction". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2404.19737](https://arxiv.org/abs/2404.19737) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  90. **^** DeepSeek-AI; et al. (2024). "DeepSeek-V3 Technical Report". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2412.19437](https://arxiv.org/abs/2412.19437) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  91. ^ _**a**_ _**b**_ Kitaev, Nikita; Kaiser, Łukasz; Levskaya, Anselm (2020). "Reformer: The Efficient Transformer". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2001.04451](https://arxiv.org/abs/2001.04451) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  92. **^** Liu, Ze; Lin, Yutong; Cao, Yue; Hu, Han; Wei, Yixuan; Zhang, Zheng; Lin, Stephen; Guo, Baining (2021). "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows". _2021 IEEE/CVF International Conference on Computer Vision (ICCV)_. IEEE. pp. 9992–10002\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2103.14030](https://arxiv.org/abs/2103.14030). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1109/ICCV48922.2021.00986](https://doi.org/10.1109%2FICCV48922.2021.00986). [ISBN](/wiki/ISBN_\(identifier\) "ISBN \(identifier\)") [978-1-6654-2812-5](/wiki/Special:BookSources/978-1-6654-2812-5 "Special:BookSources/978-1-6654-2812-5").
  93. **^** Ristea, Nicolaea Catalin; Ionescu, Radu Tudor; Khan, Fahad Shahbaz (2022-09-18). ["SepTr: Separable Transformer for Audio Spectrogram Processing"](https://www.isca-archive.org/interspeech_2022/ristea22_interspeech.html). _Interspeech_. ISCA: 4103–4107\. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2203.09581](https://arxiv.org/abs/2203.09581). [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.21437/Interspeech.2022-249](https://doi.org/10.21437%2FInterspeech.2022-249).
  94. **^** Tay, Yi; Dehghani, Mostafa; Abnar, Samira; Shen, Yikang; Bahri, Dara; Pham, Philip; Rao, Jinfeng; Yang, Liu; Ruder, Sebastian; Metzler, Donald (2020-11-08). "Long Range Arena: A Benchmark for Efficient Transformers". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2011.04006](https://arxiv.org/abs/2011.04006) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  95. **^** ["Reformer: The Efficient Transformer"](http://ai.googleblog.com/2020/01/reformer-efficient-transformer.html). _Google AI Blog_. 16 January 2020. [Archived](https://web.archive.org/web/20201022210019/https://ai.googleblog.com/2020/01/reformer-efficient-transformer.html) from the original on 2020-10-22. Retrieved 2020-10-22.
  96. **^** Gomez, Aidan N; Ren, Mengye; Urtasun, Raquel; Grosse, Roger B (2017). ["The Reversible Residual Network: Backpropagation Without Storing Activations"](https://proceedings.neurips.cc/paper/2017/hash/f9be311e65d81a9ad8150a60844bb94c-Abstract.html). _Advances in Neural Information Processing Systems_. **30**. Curran Associates, Inc. [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1707.04585](https://arxiv.org/abs/1707.04585).
  97. **^** Child, Rewon; Gray, Scott; Radford, Alec; Sutskever, Ilya (2019-04-23), _Generating Long Sequences with Sparse Transformers_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[1904.10509](https://arxiv.org/abs/1904.10509)
  98. **^** ["Constructing Transformers For Longer Sequences with Sparse Attention Methods"](https://ai.googleblog.com/2021/03/constructing-transformers-for-longer.html). _Google AI Blog_. 25 March 2021. [Archived](https://web.archive.org/web/20210918150757/https://ai.googleblog.com/2021/03/constructing-transformers-for-longer.html) from the original on 2021-09-18. Retrieved 2021-05-28.
  99. **^** Zhai, Shuangfei; Talbott, Walter; Srivastava, Nitish; Huang, Chen; Goh, Hanlin; Zhang, Ruixiang; Susskind, Josh (2021-09-21). "An Attention Free Transformer". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2105.14103](https://arxiv.org/abs/2105.14103) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  100. **^** Peng, Hao; Pappas, Nikolaos; Yogatama, Dani; Schwartz, Roy; Smith, Noah A.; Kong, Lingpeng (2021-03-19). "Random Feature Attention". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2103.02143](https://arxiv.org/abs/2103.02143) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  101. **^** Choromanski, Krzysztof; Likhosherstov, Valerii; Dohan, David; Song, Xingyou; Gane, Andreea; Sarlos, Tamas; Hawkins, Peter; Davis, Jared; Belanger, David; Colwell, Lucy; Weller, Adrian (2020-09-30). "Masked Language Modeling for Proteins via Linearly Scalable Long-Context Transformers". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2006.03555](https://arxiv.org/abs/2006.03555) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  102. **^** Lu, Kevin; Grover, Aditya; Abbeel, Pieter; Mordatch, Igor (2022-06-28). ["Frozen Pretrained Transformers as Universal Computation Engines"](https://ojs.aaai.org/index.php/AAAI/article/view/20729). _Proceedings of the AAAI Conference on Artificial Intelligence_. **36** (7): 7628–7636\. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1609/aaai.v36i7.20729](https://doi.org/10.1609%2Faaai.v36i7.20729). [ISSN](/wiki/ISSN_\(identifier\) "ISSN \(identifier\)") [2374-3468](https://search.worldcat.org/issn/2374-3468).
  103. **^** ["Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90%* ChatGPT Quality | LMSYS Org"](https://lmsys.org/blog/2023-03-30-vicuna). _lmsys.org_. Retrieved 2024-08-11.
  104. **^** Liu, Haotian; Li, Chunyuan; Wu, Qingyang; Lee, Yong Jae (2023-12-15). ["Visual Instruction Tuning"](https://proceedings.neurips.cc/paper_files/paper/2023/hash/6dcf277ea32ce3288914faf369fe6de0-Abstract-Conference.html). _Advances in Neural Information Processing Systems_. **36** : 34892–34916.
  105. **^** Radford, Alec; Kim, Jong Wook; Xu, Tao; Brockman, Greg; McLeavey, Christine; Sutskever, Ilya (2022). "Robust Speech Recognition via Large-Scale Weak Supervision". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2212.04356](https://arxiv.org/abs/2212.04356) [[eess.AS](https://arxiv.org/archive/eess.AS)].
  106. **^** Jaegle, Andrew; Gimeno, Felix; Brock, Andrew; Zisserman, Andrew; Vinyals, Oriol; Carreira, Joao (2021-06-22). "Perceiver: General Perception with Iterative Attention". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2103.03206](https://arxiv.org/abs/2103.03206) [[cs.CV](https://arxiv.org/archive/cs.CV)].
  107. **^** Jaegle, Andrew; Borgeaud, Sebastian; Alayrac, Jean-Baptiste; Doersch, Carl; Ionescu, Catalin; Ding, David; Koppula, Skanda; Zoran, Daniel; Brock, Andrew; Shelhamer, Evan; Hénaff, Olivier (2021-08-02). "Perceiver IO: A General Architecture for Structured Inputs & Outputs". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2107.14795](https://arxiv.org/abs/2107.14795) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  108. **^** ["Parti: Pathways Autoregressive Text-to-Image Model"](https://sites.research.google/parti/). _sites.research.google_. Retrieved 2024-08-09.
  109. ^ _**a**_ _**b**_ Villegas, Ruben; Babaeizadeh, Mohammad; Kindermans, Pieter-Jan; Moraldo, Hernan; Zhang, Han; Saffar, Mohammad Taghi; Castro, Santiago; Kunze, Julius; Erhan, Dumitru (2022-09-29). "Phenaki: Variable Length Video Generation from Open Domain Textual Descriptions". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2210.02399](https://arxiv.org/abs/2210.02399) [[cs.CV](https://arxiv.org/archive/cs.CV)].
  110. ^ _**a**_ _**b**_ Chang, Huiwen; Zhang, Han; Barber, Jarred; Maschinot, A. J.; Lezama, Jose; Jiang, Lu; Yang, Ming-Hsuan; Murphy, Kevin; Freeman, William T. (2023-01-02). "Muse: Text-To-Image Generation via Masked Generative Transformers". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2301.00704](https://arxiv.org/abs/2301.00704) [[cs.CV](https://arxiv.org/archive/cs.CV)].
  111. **^** Ramesh, Aditya; Pavlov, Mikhail; Goh, Gabriel; Gray, Scott; Voss, Chelsea; Radford, Alec; Chen, Mark; Sutskever, Ilya (2021-02-26), _Zero-Shot Text-to-Image Generation_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2102.12092](https://arxiv.org/abs/2102.12092)
  112. **^** Yu, Jiahui; Xu, Yuanzhong; Koh, Jing Yu; Luong, Thang; Baid, Gunjan; Wang, Zirui; Vasudevan, Vijay; Ku, Alexander; Yang, Yinfei (2022-06-21), _Scaling Autoregressive Models for Content-Rich Text-to-Image Generation_ , [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2206.10789](https://arxiv.org/abs/2206.10789)
  113. **^** Kariampuzha, William; Alyea, Gioconda; Qu, Sue; Sanjak, Jaleal; Mathé, Ewy; Sid, Eric; Chatelaine, Haley; Yadaw, Arjun; Xu, Yanji; Zhu, Qian (2023). ["Precision information extraction for rare disease epidemiology at scale"](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9972634). _Journal of Translational Medicine_. **21** (1): 157. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1186/s12967-023-04011-y](https://doi.org/10.1186%2Fs12967-023-04011-y). [PMC](/wiki/PMC_\(identifier\) "PMC \(identifier\)") [9972634](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9972634). [PMID](/wiki/PMID_\(identifier\) "PMID \(identifier\)") [36855134](https://pubmed.ncbi.nlm.nih.gov/36855134).

## Further reading

[[edit](/w/index.php?title=Transformer_\(deep_learning\)&action=edit&section=48
"Edit section: Further reading")]

  * Alexander Rush, [The Annotated transformer](https://nlp.seas.harvard.edu/2018/04/03/attention.html) [Archived](https://web.archive.org/web/20210922093841/https://nlp.seas.harvard.edu/2018/04/03/attention.html) 2021-09-22 at the [Wayback Machine](/wiki/Wayback_Machine "Wayback Machine"), Harvard NLP group, 3 April 2018
  * Phuong, Mary; Hutter, Marcus (2022). "Formal Algorithms for Transformers". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2207.09238](https://arxiv.org/abs/2207.09238) [[cs.LG](https://arxiv.org/archive/cs.LG)].
  * Ferrando, Javier; Sarti, Gabriele; Bisazza, Arianna; Costa-jussà, Marta R. (2024-05-01). "A Primer on the Inner Workings of Transformer-based Language Models". [arXiv](/wiki/ArXiv_\(identifier\) "ArXiv \(identifier\)"):[2405.00208](https://arxiv.org/abs/2405.00208) [[cs.CL](https://arxiv.org/archive/cs.CL)].
  * Leech, Gavin (2024-11-06). ["Transformer++"](https://web.archive.org/web/20250226110336/https://www.gleech.org/tplus). _argmin gravitas_. Archived from [the original](https://www.gleech.org/tplus) on 2025-02-26. Retrieved 2025-05-08.
  * Kitamura, Felipe; Moreno Júdice de Mattos Farina, Eduardo; Pedro Mazuco, João; Moy, Linda; M. Prevedello, Luciano (2025-08-25). ["Texts Are More than Notes, They Are Data: A Glimpse into How Machines Understand Text"](https://pubs.rsna.org/doi/10.1148/radiol.243217). _Radiology_. **316** (2) e243217. [doi](/wiki/Doi_\(identifier\) "Doi \(identifier\)"):[10.1148/radiol.243217](https://doi.org/10.1148%2Fradiol.243217). [PMID](/wiki/PMID_\(identifier\) "PMID \(identifier\)") [40892454](https://pubmed.ncbi.nlm.nih.gov/40892454).

  * [v](/wiki/Template:Google_AI "Template:Google AI")
  * [t](/wiki/Template_talk:Google_AI "Template talk:Google AI")
  * [e](/wiki/Special:EditPage/Template:Google_AI "Special:EditPage/Template:Google AI")

[Google AI](/wiki/Google_AI "Google AI")  
---  
  
  * [Google](/wiki/Google "Google")
  * [Google Brain](/wiki/Google_Brain "Google Brain")
  * [Google DeepMind](/wiki/Google_DeepMind "Google DeepMind")

  
Computer  
programs| | AlphaGo| | Versions| 

  * [AlphaGo](/wiki/AlphaGo "AlphaGo") (2015)
  * [Master](/wiki/Master_\(software\) "Master \(software\)") (2016)
  * [AlphaGo Zero](/wiki/AlphaGo_Zero "AlphaGo Zero") (2017)
  * [AlphaZero](/wiki/AlphaZero "AlphaZero") (2017)
  * [MuZero](/wiki/MuZero "MuZero") (2019)

  
---|---  
Competitions|

  * [Fan Hui](/wiki/AlphaGo_versus_Fan_Hui "AlphaGo versus Fan Hui") (2015)
  * [Lee Sedol](/wiki/AlphaGo_versus_Lee_Sedol "AlphaGo versus Lee Sedol") (2016)
  * [Ke Jie](/wiki/AlphaGo_versus_Ke_Jie "AlphaGo versus Ke Jie") (2017)

  
In popular culture|

  * _[AlphaGo](/wiki/AlphaGo_\(film\) "AlphaGo \(film\)")_ (2017)
  * _[The MANIAC](/wiki/The_MANIAC "The MANIAC")_ (2023)

  
  
Other|

  * [AlphaFold](/wiki/AlphaFold "AlphaFold") (2018)
  * [AlphaStar](/wiki/AlphaStar_\(software\) "AlphaStar \(software\)") (2019)
  * [AlphaDev](/wiki/AlphaDev "AlphaDev") (2023)
  * [AlphaGeometry](/wiki/AlphaGeometry "AlphaGeometry") (2024)
  * [AlphaGenome](/wiki/AlphaGenome "AlphaGenome") (2025)

  
  
Machine  
learning| | Neural networks| 

  * [Inception](/wiki/Inception_\(deep_learning_architecture\) "Inception \(deep learning architecture\)") (2014)
  * [WaveNet](/wiki/WaveNet "WaveNet") (2016)
  * [MobileNet](/wiki/MobileNet "MobileNet") (2017)
  * [Transformer](/wiki/Transformer_\(deep_learning_architecture\) "Transformer \(deep learning architecture\)") (2017)
  * [EfficientNet](/wiki/EfficientNet "EfficientNet") (2019)
  * [Gato](/wiki/Gato_\(DeepMind\) "Gato \(DeepMind\)") (2022)

  
---|---  
Other|

  * [Quantum Artificial Intelligence Lab](/wiki/Quantum_Artificial_Intelligence_Lab "Quantum Artificial Intelligence Lab")
  * [TensorFlow](/wiki/TensorFlow "TensorFlow")
  * [Tensor Processing Unit](/wiki/Tensor_Processing_Unit "Tensor Processing Unit")

  
  
Generative  
AI| | Chatbots| 

  * [Assistant](/wiki/Google_Assistant "Google Assistant") (2016)
  * [Sparrow](/wiki/Sparrow_\(chatbot\) "Sparrow \(chatbot\)") (2022)
  * [Gemini](/wiki/Google_Gemini "Google Gemini") (2023) 
    * [Nano Banana](/wiki/Nano_Banana "Nano Banana")

  
---|---  
Models|

  * [BERT](/wiki/BERT_\(language_model\) "BERT \(language model\)") (2018)
  * [XLNet](/wiki/XLNet "XLNet") (2019)
  * [T5](/wiki/T5_\(language_model\) "T5 \(language model\)") (2019)
  * [LaMDA](/wiki/LaMDA "LaMDA") (2021)
  * [Chinchilla](/wiki/Chinchilla_\(language_model\) "Chinchilla \(language model\)") (2022)
  * [PaLM](/wiki/PaLM "PaLM") (2022)
  * [Imagen](/wiki/Imagen_\(text-to-image_model\) "Imagen \(text-to-image model\)") (2023)
  * [Gemini](/wiki/Gemini_\(language_model\) "Gemini \(language model\)") (2023)
  * [VideoPoet](/wiki/VideoPoet "VideoPoet") (2024)
  * [Gemma](/wiki/Gemma_\(language_model\) "Gemma \(language model\)") (2024)
  * [Veo](/wiki/Veo_\(text-to-video_model\) "Veo \(text-to-video model\)") (2024)

  
Other|

  * [DreamBooth](/wiki/DreamBooth "DreamBooth") (2022)
  * [NotebookLM](/wiki/NotebookLM "NotebookLM") (2023)
  * [Vids](/wiki/Google_Vids "Google Vids") (2024)
  * [Gemini Robotics](/wiki/Gemini_Robotics "Gemini Robotics") (2025)

  
  
See also|

  * "[Attention Is All You Need](/wiki/Attention_Is_All_You_Need "Attention Is All You Need")"
  * [Future of Go Summit](/wiki/Future_of_Go_Summit "Future of Go Summit")
  * [Generative pre-trained transformer](/wiki/Generative_pre-trained_transformer "Generative pre-trained transformer")
  * [Google Labs](/wiki/Google_Labs "Google Labs")
  * [Google Pixel](/wiki/Google_Pixel "Google Pixel")
  * [Google Workspace](/wiki/Google_Workspace "Google Workspace")
  * [Robot Constitution](/wiki/Robot_Constitution "Robot Constitution")

  
  
  * ![](//upload.wikimedia.org/wikipedia/en/thumb/9/96/Symbol_category_class.svg/20px-Symbol_category_class.svg.png) [Category](/wiki/Category:Google_DeepMind "Category:Google DeepMind")
  * [![](//upload.wikimedia.org/wikipedia/en/thumb/4/4a/Commons-logo.svg/20px-Commons-logo.svg.png)](/wiki/File:Commons-logo.svg "Commons page") [Commons](https://commons.wikimedia.org/wiki/Category:DeepMind "commons:Category:DeepMind")

  
  
  * [v](/wiki/Template:Artificial_intelligence_navbox "Template:Artificial intelligence navbox")
  * [t](/wiki/Template_talk:Artificial_intelligence_navbox "Template talk:Artificial intelligence navbox")
  * [e](/wiki/Special:EditPage/Template:Artificial_intelligence_navbox "Special:EditPage/Template:Artificial intelligence navbox")

[Artificial intelligence](/wiki/Artificial_intelligence "Artificial
intelligence") (AI)  
---  
  
  * [History](/wiki/History_of_artificial_intelligence "History of artificial intelligence")
    * [timeline](/wiki/Timeline_of_artificial_intelligence "Timeline of artificial intelligence")
  * [Glossary](/wiki/Glossary_of_artificial_intelligence "Glossary of artificial intelligence")
  * [Companies](/wiki/List_of_artificial_intelligence_companies "List of artificial intelligence companies")
  * [Projects](/wiki/List_of_artificial_intelligence_projects "List of artificial intelligence projects")

  
Concepts|

  * [Parameter](/wiki/Parameter "Parameter")
    * [Hyperparameter](/wiki/Hyperparameter_\(machine_learning\) "Hyperparameter \(machine learning\)")
  * [Loss functions](/wiki/Loss_functions_for_classification "Loss functions for classification")
  * [Regression](/wiki/Regression_analysis "Regression analysis")
    * [Bias–variance tradeoff](/wiki/Bias%E2%80%93variance_tradeoff "Bias–variance tradeoff")
    * [Double descent](/wiki/Double_descent "Double descent")
    * [Overfitting](/wiki/Overfitting "Overfitting")
  * [Clustering](/wiki/Cluster_analysis "Cluster analysis")
  * [Gradient descent](/wiki/Gradient_descent "Gradient descent")
    * [SGD](/wiki/Stochastic_gradient_descent "Stochastic gradient descent")
    * [Quasi-Newton method](/wiki/Quasi-Newton_method "Quasi-Newton method")
    * [Conjugate gradient method](/wiki/Conjugate_gradient_method "Conjugate gradient method")
  * [Backpropagation](/wiki/Backpropagation "Backpropagation")
  * [Attention](/wiki/Attention_\(machine_learning\) "Attention \(machine learning\)")
  * [Convolution](/wiki/Convolution "Convolution")
  * [Normalization](/wiki/Normalization_\(machine_learning\) "Normalization \(machine learning\)")
    * [Batchnorm](/wiki/Batch_normalization "Batch normalization")
  * [Activation](/wiki/Activation_function "Activation function")
    * [Softmax](/wiki/Softmax_function "Softmax function")
    * [Sigmoid](/wiki/Sigmoid_function "Sigmoid function")
    * [Rectifier](/wiki/Rectifier_\(neural_networks\) "Rectifier \(neural networks\)")
  * [Gating](/wiki/Gating_mechanism "Gating mechanism")
  * [Weight initialization](/wiki/Weight_initialization "Weight initialization")
  * [Regularization](/wiki/Regularization_\(mathematics\) "Regularization \(mathematics\)")
  * [Datasets](/wiki/Training,_validation,_and_test_data_sets "Training, validation, and test data sets")
    * [Augmentation](/wiki/Data_augmentation "Data augmentation")
  * [Prompt engineering](/wiki/Prompt_engineering "Prompt engineering")
  * [Reinforcement learning](/wiki/Reinforcement_learning "Reinforcement learning")
    * [Q-learning](/wiki/Q-learning "Q-learning")
    * [SARSA](/wiki/State%E2%80%93action%E2%80%93reward%E2%80%93state%E2%80%93action "State–action–reward–state–action")
    * [Imitation](/wiki/Imitation_learning "Imitation learning")
    * [Policy gradient](/wiki/Policy_gradient_method "Policy gradient method")
  * [Diffusion](/wiki/Diffusion_process "Diffusion process")
  * [Latent diffusion model](/wiki/Latent_diffusion_model "Latent diffusion model")
  * [Autoregression](/wiki/Autoregressive_model "Autoregressive model")
  * [Adversary](/wiki/Adversarial_machine_learning "Adversarial machine learning")
  * [RAG](/wiki/Retrieval-augmented_generation "Retrieval-augmented generation")
  * [Uncanny valley](/wiki/Uncanny_valley "Uncanny valley")
  * [RLHF](/wiki/Reinforcement_learning_from_human_feedback "Reinforcement learning from human feedback")
  * [Self-supervised learning](/wiki/Self-supervised_learning "Self-supervised learning")
  * [Reflection](/wiki/Reflection_\(artificial_intelligence\) "Reflection \(artificial intelligence\)")
  * [Recursive self-improvement](/wiki/Recursive_self-improvement "Recursive self-improvement")
  * [Hallucination](/wiki/Hallucination_\(artificial_intelligence\) "Hallucination \(artificial intelligence\)")
  * [Word embedding](/wiki/Word_embedding "Word embedding")
  * [Vibe coding](/wiki/Vibe_coding "Vibe coding")
  * [Safety](/wiki/AI_safety "AI safety") ([Alignment](/wiki/AI_alignment "AI alignment"))

  
Applications|

  * [Machine learning](/wiki/Machine_learning "Machine learning")
    * [In-context learning](/wiki/Prompt_engineering#In-context_learning "Prompt engineering")
  * [Artificial neural network](/wiki/Neural_network_\(machine_learning\) "Neural network \(machine learning\)")
    * [Deep learning](/wiki/Deep_learning "Deep learning")
  * [Language model](/wiki/Language_model "Language model")
    * [Large](/wiki/Large_language_model "Large language model")
    * [NMT](/wiki/Neural_machine_translation "Neural machine translation")
    * [Reasoning](/wiki/Reasoning_model "Reasoning model")
  * [Model Context Protocol](/wiki/Model_Context_Protocol "Model Context Protocol")
  * [Intelligent agent](/wiki/Intelligent_agent "Intelligent agent")
  * [Artificial human companion](/wiki/Artificial_human_companion "Artificial human companion")
  * [Humanity's Last Exam](/wiki/Humanity%27s_Last_Exam "Humanity's Last Exam")
  * [Artificial general intelligence (AGI)](/wiki/Artificial_general_intelligence "Artificial general intelligence")

  
Implementations| | Audio–visual| 

  * [AlexNet](/wiki/AlexNet "AlexNet")
  * [WaveNet](/wiki/WaveNet "WaveNet")
  * [Human image synthesis](/wiki/Human_image_synthesis "Human image synthesis")
  * [HWR](/wiki/Handwriting_recognition "Handwriting recognition")
  * [OCR](/wiki/Optical_character_recognition "Optical character recognition")
  * [Computer vision](/wiki/Computer_vision "Computer vision")
  * [Speech synthesis](/wiki/Deep_learning_speech_synthesis "Deep learning speech synthesis")
    * [15.ai](/wiki/15.ai "15.ai")
    * [ElevenLabs](/wiki/ElevenLabs "ElevenLabs")
  * [Speech recognition](/wiki/Speech_recognition "Speech recognition")
    * [Whisper](/wiki/Whisper_\(speech_recognition_system\) "Whisper \(speech recognition system\)")
  * [Facial recognition](/wiki/Facial_recognition_system "Facial recognition system")
  * [AlphaFold](/wiki/AlphaFold "AlphaFold")
  * [Text-to-image models](/wiki/Text-to-image_model "Text-to-image model")
    * [Aurora](/wiki/Aurora_\(text-to-image_model\) "Aurora \(text-to-image model\)")
    * [DALL-E](/wiki/DALL-E "DALL-E")
    * [Firefly](/wiki/Adobe_Firefly "Adobe Firefly")
    * [Flux](/wiki/Flux_\(text-to-image_model\) "Flux \(text-to-image model\)")
    * [Ideogram](/wiki/Ideogram_\(text-to-image_model\) "Ideogram \(text-to-image model\)")
    * [Imagen](/wiki/Imagen_\(text-to-image_model\) "Imagen \(text-to-image model\)")
    * [Midjourney](/wiki/Midjourney "Midjourney")
    * [Recraft](/wiki/Recraft "Recraft")
    * [Stable Diffusion](/wiki/Stable_Diffusion "Stable Diffusion")
  * [Text-to-video models](/wiki/Text-to-video_model "Text-to-video model")
    * [Dream Machine](/wiki/Dream_Machine_\(text-to-video_model\) "Dream Machine \(text-to-video model\)")
    * [Runway Gen](/wiki/Runway_\(company\)#Services_and_technologies "Runway \(company\)")
    * [Hailuo AI](/wiki/MiniMax_\(company\)#Hailuo_AI "MiniMax \(company\)")
    * [Kling](/wiki/Kling_AI_\(company\) "Kling AI \(company\)")
    * [Sora](/wiki/Sora_\(text-to-video_model\) "Sora \(text-to-video model\)")
    * [Veo](/wiki/Veo_\(text-to-video_model\) "Veo \(text-to-video model\)")
  * [Music generation](/wiki/Music_and_artificial_intelligence "Music and artificial intelligence")
    * [Riffusion](/wiki/Riffusion "Riffusion")
    * [Suno AI](/wiki/Suno_AI "Suno AI")
    * [Udio](/wiki/Udio "Udio")

  
---|---  
Text|

  * [Word2vec](/wiki/Word2vec "Word2vec")
  * [Seq2seq](/wiki/Seq2seq "Seq2seq")
  * [GloVe](/wiki/GloVe "GloVe")
  * [BERT](/wiki/BERT_\(language_model\) "BERT \(language model\)")
  * [T5](/wiki/T5_\(language_model\) "T5 \(language model\)")
  * [Llama](/wiki/Llama_\(language_model\) "Llama \(language model\)")
  * [Chinchilla AI](/wiki/Chinchilla_\(language_model\) "Chinchilla \(language model\)")
  * [PaLM](/wiki/PaLM "PaLM")
  * [GPT](/wiki/Generative_pre-trained_transformer "Generative pre-trained transformer")
    * [1](/wiki/GPT-1 "GPT-1")
    * [2](/wiki/GPT-2 "GPT-2")
    * [3](/wiki/GPT-3 "GPT-3")
    * [J](/wiki/GPT-J "GPT-J")
    * [ChatGPT](/wiki/ChatGPT "ChatGPT")
    * [4](/wiki/GPT-4 "GPT-4")
    * [4o](/wiki/GPT-4o "GPT-4o")
    * [o1](/wiki/OpenAI_o1 "OpenAI o1")
    * [o3](/wiki/OpenAI_o3 "OpenAI o3")
    * [4.5](/wiki/GPT-4.5 "GPT-4.5")
    * [4.1](/wiki/GPT-4.1 "GPT-4.1")
    * [o4-mini](/wiki/OpenAI_o4-mini "OpenAI o4-mini")
    * [5](/wiki/GPT-5 "GPT-5")
  * [Claude](/wiki/Claude_\(language_model\) "Claude \(language model\)")
  * [Gemini](/wiki/Gemini_\(chatbot\) "Gemini \(chatbot\)")
    * [Gemini (language model)](/wiki/Gemini_\(language_model\) "Gemini \(language model\)")
    * [Gemma](/wiki/Gemma_\(language_model\) "Gemma \(language model\)")
  * [Grok](/wiki/Grok_\(chatbot\) "Grok \(chatbot\)")
  * [LaMDA](/wiki/LaMDA "LaMDA")
  * [BLOOM](/wiki/BLOOM_\(language_model\) "BLOOM \(language model\)")
  * [DBRX](/wiki/DBRX "DBRX")
  * [Project Debater](/wiki/Project_Debater "Project Debater")
  * [IBM Watson](/wiki/IBM_Watson "IBM Watson")
  * [IBM Watsonx](/wiki/IBM_Watsonx "IBM Watsonx")
  * [Granite](/wiki/IBM_Granite "IBM Granite")
  * [PanGu-Σ](/wiki/Huawei_PanGu "Huawei PanGu")
  * [DeepSeek](/wiki/DeepSeek_\(chatbot\) "DeepSeek \(chatbot\)")
  * [Qwen](/wiki/Qwen "Qwen")

  
Decisional|

  * [AlphaGo](/wiki/AlphaGo "AlphaGo")
  * [AlphaZero](/wiki/AlphaZero "AlphaZero")
  * [OpenAI Five](/wiki/OpenAI_Five "OpenAI Five")
  * [Self-driving car](/wiki/Self-driving_car "Self-driving car")
  * [MuZero](/wiki/MuZero "MuZero")
  * [Action selection](/wiki/Action_selection "Action selection")
    * [AutoGPT](/wiki/AutoGPT "AutoGPT")
  * [Robot control](/wiki/Robot_control "Robot control")

  
  
People|

  * [Alan Turing](/wiki/Alan_Turing "Alan Turing")
  * [Warren Sturgis McCulloch](/wiki/Warren_Sturgis_McCulloch "Warren Sturgis McCulloch")
  * [Walter Pitts](/wiki/Walter_Pitts "Walter Pitts")
  * [John von Neumann](/wiki/John_von_Neumann "John von Neumann")
  * [Christopher D. Manning](/wiki/Christopher_D._Manning "Christopher D. Manning")
  * [Claude Shannon](/wiki/Claude_Shannon "Claude Shannon")
  * [Shun'ichi Amari](/wiki/Shun%27ichi_Amari "Shun'ichi Amari")
  * [Kunihiko Fukushima](/wiki/Kunihiko_Fukushima "Kunihiko Fukushima")
  * [Takeo Kanade](/wiki/Takeo_Kanade "Takeo Kanade")
  * [Marvin Minsky](/wiki/Marvin_Minsky "Marvin Minsky")
  * [John McCarthy](/wiki/John_McCarthy_\(computer_scientist\) "John McCarthy \(computer scientist\)")
  * [Nathaniel Rochester](/wiki/Nathaniel_Rochester_\(computer_scientist\) "Nathaniel Rochester \(computer scientist\)")
  * [Allen Newell](/wiki/Allen_Newell "Allen Newell")
  * [Cliff Shaw](/wiki/Cliff_Shaw "Cliff Shaw")
  * [Herbert A. Simon](/wiki/Herbert_A._Simon "Herbert A. Simon")
  * [Oliver Selfridge](/wiki/Oliver_Selfridge "Oliver Selfridge")
  * [Frank Rosenblatt](/wiki/Frank_Rosenblatt "Frank Rosenblatt")
  * [Bernard Widrow](/wiki/Bernard_Widrow "Bernard Widrow")
  * [Joseph Weizenbaum](/wiki/Joseph_Weizenbaum "Joseph Weizenbaum")
  * [Seymour Papert](/wiki/Seymour_Papert "Seymour Papert")
  * [Seppo Linnainmaa](/wiki/Seppo_Linnainmaa "Seppo Linnainmaa")
  * [Paul Werbos](/wiki/Paul_Werbos "Paul Werbos")
  * [Geoffrey Hinton](/wiki/Geoffrey_Hinton "Geoffrey Hinton")
  * [John Hopfield](/wiki/John_Hopfield "John Hopfield")
  * [Jürgen Schmidhuber](/wiki/J%C3%BCrgen_Schmidhuber "Jürgen Schmidhuber")
  * [Yann LeCun](/wiki/Yann_LeCun "Yann LeCun")
  * [Yoshua Bengio](/wiki/Yoshua_Bengio "Yoshua Bengio")
  * [Lotfi A. Zadeh](/wiki/Lotfi_A._Zadeh "Lotfi A. Zadeh")
  * [Stephen Grossberg](/wiki/Stephen_Grossberg "Stephen Grossberg")
  * [Alex Graves](/wiki/Alex_Graves_\(computer_scientist\) "Alex Graves \(computer scientist\)")
  * [James Goodnight](/wiki/James_Goodnight "James Goodnight")
  * [Andrew Ng](/wiki/Andrew_Ng "Andrew Ng")
  * [Fei-Fei Li](/wiki/Fei-Fei_Li "Fei-Fei Li")
  * [Alex Krizhevsky](/wiki/Alex_Krizhevsky "Alex Krizhevsky")
  * [Ilya Sutskever](/wiki/Ilya_Sutskever "Ilya Sutskever")
  * [Oriol Vinyals](/wiki/Oriol_Vinyals "Oriol Vinyals")
  * [Quoc V. Le](/wiki/Quoc_V._Le "Quoc V. Le")
  * [Ian Goodfellow](/wiki/Ian_Goodfellow "Ian Goodfellow")
  * [Demis Hassabis](/wiki/Demis_Hassabis "Demis Hassabis")
  * [David Silver](/wiki/David_Silver_\(computer_scientist\) "David Silver \(computer scientist\)")
  * [Andrej Karpathy](/wiki/Andrej_Karpathy "Andrej Karpathy")
  * [Ashish Vaswani](/wiki/Ashish_Vaswani "Ashish Vaswani")
  * [Noam Shazeer](/wiki/Noam_Shazeer "Noam Shazeer")
  * [Aidan Gomez](/wiki/Aidan_Gomez "Aidan Gomez")
  * [John Schulman](/wiki/John_Schulman "John Schulman")
  * [Mustafa Suleyman](/wiki/Mustafa_Suleyman "Mustafa Suleyman")
  * [Jan Leike](/wiki/Jan_Leike "Jan Leike")
  * [Daniel Kokotajlo](/wiki/Daniel_Kokotajlo_\(researcher\) "Daniel Kokotajlo \(researcher\)")
  * [François Chollet](/wiki/Fran%C3%A7ois_Chollet "François Chollet")

  
Architectures|

  * [Neural Turing machine](/wiki/Neural_Turing_machine "Neural Turing machine")
  * [Differentiable neural computer](/wiki/Differentiable_neural_computer "Differentiable neural computer")
  * [Transformer](/wiki/Transformer_\(deep_learning_architecture\) "Transformer \(deep learning architecture\)")
    * [Vision transformer (ViT)](/wiki/Vision_transformer "Vision transformer")
  * [Recurrent neural network (RNN)](/wiki/Recurrent_neural_network "Recurrent neural network")
  * [Long short-term memory (LSTM)](/wiki/Long_short-term_memory "Long short-term memory")
  * [Gated recurrent unit (GRU)](/wiki/Gated_recurrent_unit "Gated recurrent unit")
  * [Echo state network](/wiki/Echo_state_network "Echo state network")
  * [Multilayer perceptron (MLP)](/wiki/Multilayer_perceptron "Multilayer perceptron")
  * [Convolutional neural network (CNN)](/wiki/Convolutional_neural_network "Convolutional neural network")
  * [Residual neural network (RNN)](/wiki/Residual_neural_network "Residual neural network")
  * [Highway network](/wiki/Highway_network "Highway network")
  * [Mamba](/wiki/Mamba_\(deep_learning_architecture\) "Mamba \(deep learning architecture\)")
  * [Autoencoder](/wiki/Autoencoder "Autoencoder")
  * [Variational autoencoder (VAE)](/wiki/Variational_autoencoder "Variational autoencoder")
  * [Generative adversarial network (GAN)](/wiki/Generative_adversarial_network "Generative adversarial network")
  * [Graph neural network (GNN)](/wiki/Graph_neural_network "Graph neural network")

  
  
  * ![](//upload.wikimedia.org/wikipedia/en/thumb/9/96/Symbol_category_class.svg/20px-Symbol_category_class.svg.png) [Category](/wiki/Category:Artificial_intelligence "Category:Artificial intelligence")

  
  
![](https://en.wikipedia.org/wiki/Special:CentralAutoLogin/start?useformat=desktop&type=1x1&usesul3=1)

Retrieved from
"[https://en.wikipedia.org/w/index.php?title=Transformer_(deep_learning)&oldid=1321325230](https://en.wikipedia.org/w/index.php?title=Transformer_\(deep_learning\)&oldid=1321325230)"

[Categories](/wiki/Help:Category "Help:Category"):

  * [Google software](/wiki/Category:Google_software "Category:Google software")
  * [Neural network architectures](/wiki/Category:Neural_network_architectures "Category:Neural network architectures")
  * [2017 in artificial intelligence](/wiki/Category:2017_in_artificial_intelligence "Category:2017 in artificial intelligence")

Hidden categories:

  * [Articles with short description](/wiki/Category:Articles_with_short_description "Category:Articles with short description")
  * [Short description is different from Wikidata](/wiki/Category:Short_description_is_different_from_Wikidata "Category:Short description is different from Wikidata")
  * [Webarchive template wayback links](/wiki/Category:Webarchive_template_wayback_links "Category:Webarchive template wayback links")

  * This page was last edited on 9 November 2025, at 22:54 (UTC).
  * Text is available under the [Creative Commons Attribution-ShareAlike 4.0 License](/wiki/Wikipedia:Text_of_the_Creative_Commons_Attribution-ShareAlike_4.0_International_License "Wikipedia:Text of the Creative Commons Attribution-ShareAlike 4.0 International License"); additional terms may apply. By using this site, you agree to the [Terms of Use](https://foundation.wikimedia.org/wiki/Special:MyLanguage/Policy:Terms_of_Use "foundation:Special:MyLanguage/Policy:Terms of Use") and [Privacy Policy](https://foundation.wikimedia.org/wiki/Special:MyLanguage/Policy:Privacy_policy "foundation:Special:MyLanguage/Policy:Privacy policy"). Wikipedia® is a registered trademark of the [Wikimedia Foundation, Inc.](https://wikimediafoundation.org/), a non-profit organization.

  * [Privacy policy](https://foundation.wikimedia.org/wiki/Special:MyLanguage/Policy:Privacy_policy)
  * [About Wikipedia](/wiki/Wikipedia:About)
  * [Disclaimers](/wiki/Wikipedia:General_disclaimer)
  * [Contact Wikipedia](//en.wikipedia.org/wiki/Wikipedia:Contact_us)
  * [Code of Conduct](https://foundation.wikimedia.org/wiki/Special:MyLanguage/Policy:Universal_Code_of_Conduct)
  * [Developers](https://developer.wikimedia.org)
  * [Statistics](https://stats.wikimedia.org/#/en.wikipedia.org)
  * [Cookie statement](https://foundation.wikimedia.org/wiki/Special:MyLanguage/Policy:Cookie_statement)
  * [Mobile view](//en.wikipedia.org/w/index.php?title=Transformer_\(deep_learning\)&mobileaction=toggle_view_mobile)

  * [![Wikimedia Foundation](/static/images/footer/wikimedia.svg)](https://www.wikimedia.org/)
  * [![Powered by MediaWiki](/w/resources/assets/mediawiki_compact.svg)](https://www.mediawiki.org/)

Search

Search

Toggle the table of contents

Transformer (deep learning)

30 languages Add topic

  *[v]: View this template
  *[t]: Discuss this template
  *[e]: Edit this template

